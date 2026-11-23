"""Tests del servidor MCP universal.

Se prueba el **protocolo** (JSON-RPC 2.0) a través del dispatcher, que es la
capa compartida por el SDK oficial y el fallback propio: así se verifica el
comportamiento observable con cualquiera de los dos transportes.

También se prueba el servidor por ``stdio`` de extremo a extremo (proceso
real, JSON Lines), que es como lo consume un cliente MCP.
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))  # para importar 'tests.support'
sys.path.insert(0, str(BASE / "src"))

from qetgen.mcp_server.dispatch import Dispatcher, handle_line  # noqa: E402
from qetgen.mcp_server.fallback import serve_stdio  # noqa: E402
from qetgen.mcp_server.prompts import get_prompt, list_prompts  # noqa: E402
from qetgen.mcp_server.resources import list_resources, read_resource  # noqa: E402
from qetgen.mcp_server.session import Session, ToolError  # noqa: E402
from qetgen.mcp_server.tools import TOOLS, call_tool, list_tools  # noqa: E402
from tests.support import FIXTURE_LIBRARY  # noqa: E402


def make_session() -> Session:
    """Sesión con el catálogo real de símbolos y la configuración central.

    Usa la biblioteca de fixtures para no depender de que QElectroTech esté
    instalado en la máquina que ejecuta los tests.
    """
    return Session.create(library_path=FIXTURE_LIBRARY)


class TestHerramientas(unittest.TestCase):

    def test_las_ocho_herramientas_estan_publicadas(self):
        names = {tool["name"] for tool in list_tools()}
        self.assertEqual(names, {
            "crear_diagrama", "listar_simbolos", "agregar_elemento",
            "conectar_elementos", "ejecutar_auto_layout", "validar_estetica",
            "obtener_resumen_canvas", "exportar_archivo"})

    def test_cada_herramienta_publica_un_esquema_typed(self):
        for tool in list_tools():
            schema = tool["inputSchema"]
            self.assertEqual(schema.get("type"), "object", tool["name"])
            self.assertIn("properties", schema)
            self.assertFalse(schema.get("additionalProperties", True),
                             f"{tool['name']} debe rechazar claves desconocidas")

    def test_crear_diagrama_crea_un_proyecto(self):
        session = make_session()
        result = call_tool(session, "crear_diagrama",
                           {"titulo": "PRUEBA", "formato_hoja": "A3_17x8"})
        self.assertEqual(result["titulo"], "PRUEBA")
        self.assertEqual(result["folios"], 1)
        self.assertIsNotNone(session.project)

    def test_crear_diagrama_rechaza_un_formato_desconocido(self):
        session = make_session()
        with self.assertRaises(ToolError) as ctx:
            call_tool(session, "crear_diagrama",
                      {"titulo": "X", "formato_hoja": "A9_99x99"})
        self.assertIn("formato de hoja desconocido", str(ctx.exception))

    def test_listar_simbolos_devuelve_geometria(self):
        session = make_session()
        result = call_tool(session, "listar_simbolos", {"tipo": "lamp"})
        self.assertEqual(result["total"], 1)
        symbol = result["simbolos"][0]
        self.assertEqual(symbol["tipo"], "lamp")
        self.assertIn("caja_reservada", symbol)
        self.assertIn("caja_tinta", symbol)

    def test_agregar_elemento_y_conectar(self):
        session = make_session()
        call_tool(session, "crear_diagrama", {"titulo": "PRUEBA"})
        call_tool(session, "agregar_elemento",
                  {"id": "A", "tipo": "lamp", "x": 200, "y": 200})
        call_tool(session, "agregar_elemento",
                  {"id": "B", "tipo": "lamp", "x": 500, "y": 200})
        result = call_tool(session, "conectar_elementos",
                           {"desde": "A", "hasta": "B"})
        self.assertEqual(result["clave"], "A[0] -> B[0]")
        summary = call_tool(session, "obtener_resumen_canvas", {})
        self.assertEqual(summary["elementos"], 2)
        self.assertEqual(summary["conexiones"], 1)

    def test_ids_duplicados_son_un_error_accionable(self):
        session = make_session()
        call_tool(session, "crear_diagrama", {"titulo": "PRUEBA"})
        call_tool(session, "agregar_elemento",
                  {"id": "A", "tipo": "lamp", "x": 200, "y": 200})
        with self.assertRaises(ToolError) as ctx:
            call_tool(session, "agregar_elemento",
                      {"id": "A", "tipo": "lamp", "x": 300, "y": 300})
        self.assertIn("únicos", str(ctx.exception))

    def test_conectar_a_un_elemento_inexistente_falla(self):
        session = make_session()
        call_tool(session, "crear_diagrama", {"titulo": "PRUEBA"})
        call_tool(session, "agregar_elemento",
                  {"id": "A", "tipo": "lamp", "x": 200, "y": 200})
        with self.assertRaises(ToolError) as ctx:
            call_tool(session, "conectar_elementos",
                      {"desde": "A", "hasta": "FANTASMA"})
        self.assertIn("no existe", str(ctx.exception))

    def test_una_terminal_inexistente_falla(self):
        session = make_session()
        call_tool(session, "crear_diagrama", {"titulo": "PRUEBA"})
        call_tool(session, "agregar_elemento",
                  {"id": "A", "tipo": "lamp", "x": 200, "y": 200})
        call_tool(session, "agregar_elemento",
                  {"id": "B", "tipo": "lamp", "x": 500, "y": 200})
        with self.assertRaises(ToolError) as ctx:
            call_tool(session, "conectar_elementos",
                      {"desde": "A", "hasta": "B", "terminal_desde": 9})
        self.assertIn("terminal", str(ctx.exception).lower())

    def test_auto_layout_en_simulacion_no_modifica(self):
        session = make_session()
        call_tool(session, "crear_diagrama", {"titulo": "PRUEBA"})
        call_tool(session, "agregar_elemento",
                  {"id": "A", "tipo": "lamp", "x": 123, "y": 457})
        before = session.project.elements[0].x
        result = call_tool(session, "ejecutar_auto_layout",
                           {"aplicar": False})
        self.assertFalse(result["aplicado"])
        self.assertEqual(session.project.elements[0].x, before)

    def test_auto_layout_aplicado_mueve_los_bloqueados_no(self):
        session = make_session()
        call_tool(session, "crear_diagrama", {"titulo": "PRUEBA"})
        call_tool(session, "agregar_elemento",
                  {"id": "A", "tipo": "lamp", "x": 123, "y": 456,
                   "bloqueado": True})
        call_tool(session, "agregar_elemento",
                  {"id": "B", "tipo": "lamp", "x": 200, "y": 100})
        result = call_tool(session, "ejecutar_auto_layout", {"aplicar": True})
        self.assertEqual(result["locked"], 1)
        self.assertEqual(session.project.elements[0].x, 123)
        self.assertEqual(session.project.elements[0].y, 456)

    def test_validar_estetica_devuelve_diagnosticos(self):
        session = make_session()
        call_tool(session, "crear_diagrama", {"titulo": "PRUEBA"})
        call_tool(session, "agregar_elemento",
                  {"id": "A", "tipo": "lamp", "x": 200, "y": 200})
        call_tool(session, "agregar_elemento",
                  {"id": "B", "tipo": "lamp", "x": 205, "y": 205})
        result = call_tool(session, "validar_estetica", {})
        self.assertFalse(result["ok"])
        codes = [issue["code"] for issue in result["estetica"]["issues"]]
        self.assertIn("SYMBOL_OVERLAP", codes)

    def test_exportar_archivo_escribe_un_qet_valido(self):
        import xml.etree.ElementTree as ET

        session = make_session()
        call_tool(session, "crear_diagrama", {"titulo": "PRUEBA"})
        call_tool(session, "agregar_elemento",
                  {"id": "A", "type" if False else "tipo": "lamp",
                   "x": 200, "y": 200})
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "salida.qet"
            result = call_tool(session, "exportar_archivo",
                               {"ruta": str(target), "formato": "qet"})
            self.assertTrue(target.is_file())
            self.assertGreater(result["bytes"], 0)
            root = ET.parse(target).getroot()
            self.assertEqual(root.tag, "project")

    def test_una_herramienta_inexistente_es_un_error_claro(self):
        session = make_session()
        with self.assertRaises(ToolError) as ctx:
            call_tool(session, "no_existe", {})
        self.assertIn("Herramienta desconocida", str(ctx.exception))

    def test_una_entrada_invalida_es_un_error_claro(self):
        session = make_session()
        with self.assertRaises(ToolError) as ctx:
            call_tool(session, "crear_diagrama", {"titulo": ""})
        self.assertIn("Entrada inválida", str(ctx.exception))

    def test_una_clave_desconocida_es_rechazada(self):
        session = make_session()
        with self.assertRaises(ToolError):
            call_tool(session, "crear_diagrama",
                      {"titulo": "X", "columna_inventada": 1})


class TestRecursosYPrompts(unittest.TestCase):

    def test_los_cuatro_recursos_estan_publicados(self):
        uris = {resource["uri"] for resource in list_resources()}
        self.assertEqual(uris, {
            "qetgen://catalogo", "qetgen://config",
            "qetgen://formatos-hoja", "qetgen://proyecto"})

    def test_leer_el_catalogo(self):
        session = make_session()
        payload = read_resource(session, "qetgen://catalogo")
        data = json.loads(payload["contents"][0]["text"])
        self.assertIn("lamp", data)
        self.assertIn("caja_reservada", data["lamp"])

    def test_leer_el_proyecto_sin_proyecto_da_error(self):
        session = make_session()
        with self.assertRaises(ToolError):
            read_resource(session, "qetgen://proyecto")

    def test_los_dos_prompts_estan_publicados(self):
        names = {prompt["name"] for prompt in list_prompts()}
        self.assertEqual(names, {"system_prompt", "revisar_plano"})

    def test_el_system_prompt_menciona_las_reglas_clave(self):
        session = make_session()
        payload = get_prompt(session, "system_prompt", {})
        text = payload["messages"][0]["content"]["text"]
        self.assertIn("PENDIENTE DE VERIFICACIÓN", text)
        self.assertIn("bloqueado", text)
        self.assertIn("validar_estetica", text)


class TestProtocolo(unittest.TestCase):

    def setUp(self):
        self.dispatcher = Dispatcher(make_session(), server_version="test")

    def test_initialize_responde_con_el_protocolo(self):
        response = self.dispatcher.handle({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"}})
        result = response["result"]
        self.assertEqual(result["protocolVersion"], "2024-11-05")
        self.assertEqual(result["serverInfo"]["name"], "qetgen")
        self.assertIn("tools", result["capabilities"])

    def test_una_notificacion_no_tiene_respuesta(self):
        response = self.dispatcher.handle({
            "jsonrpc": "2.0", "method": "notifications/initialized"})
        self.assertIsNone(response)

    def test_tools_list(self):
        response = self.dispatcher.handle(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(len(response["result"]["tools"]), len(TOOLS))

    def test_tools_call_devuelve_contenido_y_estructura(self):
        response = self.dispatcher.handle({
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "crear_diagrama",
                       "arguments": {"titulo": "X"}}})
        result = response["result"]
        self.assertFalse(result["isError"])
        self.assertEqual(result["content"][0]["type"], "text")
        self.assertIn("titulo", result["structuredContent"])

    def test_un_error_de_herramienta_es_isError_no_error_de_protocolo(self):
        self.dispatcher.handle({
            "jsonrpc": "2.0", "id": 0, "method": "tools/call",
            "params": {"name": "crear_diagrama", "arguments": {"titulo": "X"}}})
        response = self.dispatcher.handle({
            "jsonrpc": "2.0", "id": 4, "method": "tools/call",
            "params": {"name": "agregar_elemento",
                       "arguments": {"id": "A", "tipo": "no_existe",
                                     "x": 1, "y": 1}}})
        result = response["result"]
        self.assertTrue(result["isError"])
        self.assertIn("no_existe", result["content"][0]["text"])

    def test_un_metodo_desconocido_da_error_jsonrpc(self):
        response = self.dispatcher.handle(
            {"jsonrpc": "2.0", "id": 5, "method": "inventado"})
        self.assertIn("error", response)
        self.assertIn("Método no soportado", response["error"]["message"])

    def test_un_json_invalido_da_error_de_parseo(self):
        response = handle_line(self.dispatcher, "{no es json")
        self.assertEqual(response["error"]["code"], -32700)


class TestServidorStdio(unittest.TestCase):
    """El servidor por stdio, como lo consume un cliente MCP real."""

    def test_ciclo_completo_por_stdio(self):
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2024-11-05"}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "crear_diagrama",
                        "arguments": {"titulo": "DESDE STDIO"}}},
        ]
        stdin = io.StringIO("\n".join(json.dumps(r) for r in requests) + "\n")
        stdout = io.StringIO()
        handled = serve_stdio(make_session(), stdin=stdin, stdout=stdout)
        self.assertEqual(handled, 3)
        responses = [json.loads(line) for line in stdout.getvalue().splitlines()]
        self.assertEqual(len(responses), 3)
        self.assertEqual(responses[2]["result"]["structuredContent"]["titulo"],
                         "DESDE STDIO")

    def test_el_proceso_real_responde_por_stdio(self):
        """Prueba de extremo a extremo: `qetgen serve --fallback`."""
        request = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        result = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "qetgen.cli", "serve",
             "--fallback", "--library", str(FIXTURE_LIBRARY)],
            input=json.dumps(request) + "\n", capture_output=True, text=True,
            encoding="utf-8", cwd=str(BASE))
        self.assertEqual(result.returncode, 0, result.stderr[:2000])
        payload = json.loads(result.stdout.splitlines()[0])
        self.assertEqual(len(payload["result"]["tools"]), len(TOOLS))


if __name__ == "__main__":
    unittest.main()
