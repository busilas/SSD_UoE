import pytest
import pycodestyle
import bandit
from bandit.core import manager
from bandit.core import config
from pylint.lint import Run
import astroid
import os
import re

class TestCodeQuality:
    """Test suite for code quality checks using various linters"""
    
    def setup_method(self):
        self.file_path = "your_python_file.py"  # Make sure the file exists or update this path
        self.max_line_length = 100
        
    def test_pylint(self):
        """Test code quality using pylint"""
        # Run pylint without `do_exit`
        result = Run([self.file_path, '--disable=C0111,C0103'])

        # Get the score from pylint output
        output = result.linter.reporter.messages
        score_match = re.search(r'Your code has been rated at ([-\d.]+)', output)
        if score_match:
            score = float(score_match.group(1))
            # Ensure minimum score of 8.0
            assert score >= 8.0, f"Pylint score {score} is below minimum threshold of 8.0"

        # Check for critical errors
        assert "error" not in output.lower(), f"Pylint found errors:\n{output}"

    def test_pycodestyle(self):
        """Test PEP 8 compliance using pycodestyle"""
        style_guide = pycodestyle.StyleGuide(
            max_line_length=self.max_line_length,
            ignore=['E402']  # Ignore module level import not at top of file
        )

        result = style_guide.check_files([self.file_path])

        # Print the error details for debugging
        print(f"Found {result.total_errors} style errors: {result.get_statistics()}")

        # Assert no style errors
        assert result.total_errors == 0, f"Found {result.total_errors} style errors"

    def test_bandit_security(self):
        """Test for security issues using Bandit"""
        # Initialize Bandit with a config
        config_data = config.Config()
        b_mgr = manager.BanditManager(
            config=config_data,
            agg_type='file', 
            debug=False,
            verbose=False,
            quiet=True,
            profile=None,
        )

        # Run Bandit analysis
        b_mgr.discover_files([self.file_path])
        b_mgr.run_tests()

        # Check results
        results = b_mgr.get_issue_list()
        high_severity_issues = [r for r in results if r.severity >= 2]  # High and Critical

        assert len(high_severity_issues) == 0, (
            f"Found {len(high_severity_issues)} high/critical security issues"
        )

    def test_import_order(self):
        """Test proper import ordering"""
        with open(self.file_path, 'r') as file:
            content = file.read()
        
        # Get all import statements
        import_lines = re.findall(r'^(?:from|import)\s+.*$', content, re.MULTILINE)
        
        # Check that stdlib imports come before third-party imports
        stdlib_modules = set([
            'datetime', 'uuid', 'logging', 'json', 'threading',
            'unittest', 'functools', 'enum'
        ])
        
        found_third_party = False
        for line in import_lines:
            module = line.split()[1].split('.')[0]
            
            if module in stdlib_modules:
                assert not found_third_party, (
                    f"Standard library import '{line}' after third-party imports"
                )
            else:
                found_third_party = True

    def test_class_naming(self):
        """Test class naming conventions"""
        module = astroid.parse(open(self.file_path).read())
        
        for node in module.nodes_of_class(astroid.ClassDef):
            # Classes should use CamelCase
            assert node.name[0].isupper(), f"Class {node.name} should use CamelCase"
            assert '_' not in node.name, f"Class {node.name} should use CamelCase, not snake_case"

    def test_function_naming(self):
        """Test function naming conventions"""
        module = astroid.parse(open(self.file_path).read())
        
        for node in module.nodes_of_class(astroid.FunctionDef):
            # Functions should use snake_case
            assert node.name.islower() or '_' in node.name, (
                f"Function {node.name} should use snake_case"
            )
            assert not node.name[0].isupper(), (
                f"Function {node.name} should not start with uppercase"
            )

    def test_docstring_presence(self):
        """Test presence of docstrings"""
        module = astroid.parse(open(self.file_path).read())
        
        # Check classes
        for node in module.nodes_of_class(astroid.ClassDef):
            assert isinstance(node.doc, str) and node.doc.strip(), (
                f"Class {node.name} missing docstring"
            )
            
        # Check methods and functions
        for node in module.nodes_of_class(astroid.FunctionDef):
            # Skip private methods
            if not node.name.startswith('_'):
                assert isinstance(node.doc, str) and node.doc.strip(), (
                    f"Function {node.name} missing docstring"
                )

    def test_complexity(self):
        """Test code complexity metrics"""
        module = astroid.parse(open(self.file_path).read())
        
        for node in module.nodes_of_class(astroid.FunctionDef):
            # Count number of branches (if/for/while statements)
            branches = len([child for child in node.nodes_of_class((
                astroid.If, astroid.For, astroid.While
            ))])
            
            # Ensure reasonable complexity
            assert branches <= 10, (
                f"Function {node.name} is too complex with {branches} branches"
            )

    def test_line_length(self):
        """Test line length compliance"""
        with open(self.file_path, 'r') as file:
            for i, line in enumerate(file, 1):
                assert len(line) <= self.max_line_length, (
                    f"Line {i} exceeds {self.max_line_length} characters"
                )

    def test_exception_handling(self):
        """Test proper exception handling"""
        module = astroid.parse(open(self.file_path).read())
        
        for node in module.nodes_of_class(astroid.ExceptHandler):
            # Ensure we're not using bare except
            assert node.type is not None, "Found bare except clause"
            
            # Ensure we're not just passing in except blocks
            if isinstance(node.body[0], astroid.Pass):
                assert len(node.body) > 1, "Found except block with only pass"

if __name__ == '__main__':
    pytest.main([__file__])
