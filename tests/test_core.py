import unittest
from assayflux.lexer import Lexer, LexError
from assayflux.generator.sql_generator import SQLGenerator
from assayflux.interop.runtime import InteropRuntimeRegistry


class TestAssayFluxCoreUpgrades(unittest.TestCase):
    
    def test_lexer_error_reporting(self):
        lexer = Lexer("var x = $;", filename="test.af")
        with self.assertRaises(LexError) as ctx:
            lexer.tokenize()
        self.assertIn("test.af", str(ctx.exception))
        self.assertIn("Lexical Error", str(ctx.exception))

    def test_sql_generator_sanitization(self):
        gen = SQLGenerator(ast=None)
        self.assertEqual(gen.escape_identifier("users_table"), '"users_table"')
        
        with self.assertRaises(ValueError):
            gen.escape_identifier("users; DROP TABLE users;")
            
        self.assertEqual(gen.sanitize_value("admin' OR '1'='1"), "'admin'' OR ''1''=''1'")
        self.assertEqual(gen.sanitize_value(100), "100")
        self.assertEqual(gen.sanitize_value(True), "TRUE")
        self.assertEqual(gen.sanitize_value(None), "NULL")

    def test_interop_runtime_type_safety(self):
        registry = InteropRuntimeRegistry()
        
        # Test invalid callable registration
        with self.assertRaises(TypeError):
            registry.register("python", "not-a-callable")
            
        # Test unregistered language execution
        with self.assertRaises(KeyError):
            registry.execute("rust", {"data": 123})
            
        # Test valid registration and execution
        mock_handler = lambda p: p.get("val", 0) * 2
        registry.register("python", mock_handler)
        
        result = registry.execute("python", {"val": 21})
        self.assertEqual(result, 42)
        
        # Test invalid payload type contract
        with self.assertRaises(TypeError):
            registry.execute("python", "invalid-payload-type")


if __name__ == "__main__":
    unittest.main()
