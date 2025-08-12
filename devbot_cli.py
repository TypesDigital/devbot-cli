#!/usr/bin/env python3
"""
DevBot CLI - AI-powered chatbot for developers
A comprehensive CLI tool for chat, code execution, and code improvement
"""

import os
import sys
import json
import subprocess
import tempfile
import argparse
import readline
from datetime import datetime
from pathlib import Path
import requests
from typing import Dict, List, Optional, Tuple

class CodeRunner:
    """Handles code execution in different languages"""
    
    SUPPORTED_LANGUAGES = {
        'python': {'ext': '.py', 'cmd': 'python3'},
        'javascript': {'ext': '.js', 'cmd': 'node'},
        'java': {'ext': '.java', 'cmd': 'javac'},
        'cpp': {'ext': '.cpp', 'cmd': 'g++'},
        'c': {'ext': '.c', 'cmd': 'gcc'},
        'go': {'ext': '.go', 'cmd': 'go run'},
        'rust': {'ext': '.rs', 'cmd': 'rustc'},
        'bash': {'ext': '.sh', 'cmd': 'bash'},
    }
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def run_code(self, code: str, language: str) -> Tuple[str, str, int]:
        """Execute code and return output, error, and return code"""
        if language not in self.SUPPORTED_LANGUAGES:
            return "", f"Unsupported language: {language}", 1
        
        lang_config = self.SUPPORTED_LANGUAGES[language]
        filename = f"temp_code{lang_config['ext']}"
        filepath = os.path.join(self.temp_dir, filename)
        
        try:
            # Write code to file
            with open(filepath, 'w') as f:
                f.write(code)
            
            # Handle compiled languages
            if language in ['java', 'cpp', 'c', 'rust']:
                return self._run_compiled_code(filepath, language, lang_config)
            else:
                return self._run_interpreted_code(filepath, lang_config)
                
        except Exception as e:
            return "", str(e), 1
    
    def _run_compiled_code(self, filepath: str, language: str, config: Dict) -> Tuple[str, str, int]:
        """Handle compiled languages"""
        if language == 'java':
            # Compile Java
            compile_result = subprocess.run(['javac', filepath], 
                                         capture_output=True, text=True)
            if compile_result.returncode != 0:
                return "", compile_result.stderr, compile_result.returncode
            
            # Run Java
            class_name = Path(filepath).stem
            result = subprocess.run(['java', '-cp', os.path.dirname(filepath), class_name],
                                  capture_output=True, text=True, timeout=30)
        
        elif language in ['cpp', 'c']:
            # Compile C/C++
            output_file = filepath.replace(config['ext'], '')
            compile_result = subprocess.run([config['cmd'], filepath, '-o', output_file],
                                         capture_output=True, text=True)
            if compile_result.returncode != 0:
                return "", compile_result.stderr, compile_result.returncode
            
            # Run executable
            result = subprocess.run([output_file], capture_output=True, text=True, timeout=30)
        
        elif language == 'rust':
            # Compile Rust
            output_file = filepath.replace('.rs', '')
            compile_result = subprocess.run(['rustc', filepath, '-o', output_file],
                                         capture_output=True, text=True)
            if compile_result.returncode != 0:
                return "", compile_result.stderr, compile_result.returncode
            
            # Run executable
            result = subprocess.run([output_file], capture_output=True, text=True, timeout=30)
        
        return result.stdout, result.stderr, result.returncode
    
    def _run_interpreted_code(self, filepath: str, config: Dict) -> Tuple[str, str, int]:
        """Handle interpreted languages"""
        cmd = [config['cmd'], filepath]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout, result.stderr, result.returncode

class AIAssistant:
    """Mock AI assistant - replace with actual AI API integration"""
    
    def __init__(self):
        self.conversation_history = []
    
    def chat(self, message: str, context: str = "") -> str:
        """Process chat message and return response"""
        # This is a mock implementation
        # In a real implementation, you would integrate with OpenAI, Anthropic, or other AI APIs
        
        self.conversation_history.append({"role": "user", "content": message})
        
        # Simple pattern matching for demo purposes
        if "help" in message.lower():
            response = """DevBot Commands:
• /run <language> - Run code in specified language
• /improve <file> - Get code improvement suggestions  
• /explain <code> - Explain code functionality
• /debug - Help debug issues
• /exit - Exit the chat
• Just type normally for general conversation!"""
        
        elif "run" in message.lower() and "code" in message.lower():
            response = "I can help you run code! Use the /run command followed by the language name."
        
        elif "improve" in message.lower():
            response = "I can analyze your code and suggest improvements for performance, readability, and best practices."
        
        elif any(lang in message.lower() for lang in ['python', 'javascript', 'java', 'cpp', 'go', 'rust']):
            response = f"Great! I can help you with that programming language. What would you like to do?"
        
        else:
            response = "I'm DevBot, your AI coding assistant! I can help with code execution, improvements, debugging, and general programming questions. How can I assist you today?"
        
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def analyze_code(self, code: str, language: str) -> str:
        """Analyze code and provide improvement suggestions"""
        suggestions = []
        
        # Basic code analysis patterns (replace with AI analysis)
        if language == 'python':
            if 'print(' in code and code.count('print(') > 3:
                suggestions.append("Consider using logging instead of multiple print statements")
            if 'for i in range(len(' in code:
                suggestions.append("Consider using 'for item in list' instead of index-based iteration")
        
        elif language == 'javascript':
            if 'var ' in code:
                suggestions.append("Consider using 'let' or 'const' instead of 'var'")
            if '== ' in code:
                suggestions.append("Consider using strict equality (===) instead of loose equality (==)")
        
        if not suggestions:
            suggestions.append(f"Code looks good! Following {language} best practices.")
        
        return "\n".join([f"• {suggestion}" for suggestion in suggestions])

class DevBotCLI:
    """Main CLI application"""
    
    def __init__(self):
        self.code_runner = CodeRunner()
        self.ai_assistant = AIAssistant()
        self.config_dir = Path.home() / '.devbot'
        self.config_file = self.config_dir / 'config.json'
        self.history_file = self.config_dir / 'history.json'
        self.setup_config()
    
    def setup_config(self):
        """Initialize configuration"""
        self.config_dir.mkdir(exist_ok=True)
        
        if not self.config_file.exists():
            default_config = {
                'default_language': 'python',
                'auto_save_history': True,
                'max_output_lines': 50,
                'timeout': 30
            }
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
        
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
    
    def save_history(self, command: str, result: str):
        """Save command history"""
        if not self.config.get('auto_save_history', True):
            return
        
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'result': result[:500] + '...' if len(result) > 500 else result
        }
        
        history = []
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        
        history.append(history_entry)
        
        # Keep only last 100 entries
        if len(history) > 100:
            history = history[-100:]
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def print_banner(self):
        """Display welcome banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                        🤖 DevBot CLI                         ║
║                   AI Assistant for Developers                 ║
║                                                               ║
║  Features:                                                    ║
║  • 💬 AI-powered chat assistance                             ║
║  • 🏃 Multi-language code execution                          ║
║  • 📈 Code improvement suggestions                           ║
║  • 🐛 Debugging help                                         ║
║  • 📚 Code explanation                                       ║
║                                                               ║
║  Type '/help' for commands or just start chatting!           ║
╚═══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def handle_run_command(self, args: List[str]) -> str:
        """Handle code execution command"""
        if len(args) < 1:
            return "Usage: /run <language> [file_path]\nSupported: " + ", ".join(self.code_runner.SUPPORTED_LANGUAGES.keys())
        
        language = args[0].lower()
        
        if len(args) > 1:
            # Run from file
            file_path = args[1]
            if not os.path.exists(file_path):
                return f"File not found: {file_path}"
            
            with open(file_path, 'r') as f:
                code = f.read()
        else:
            # Interactive code input
            print(f"Enter your {language} code (press Ctrl+D or type 'EOF' on a new line to finish):")
            code_lines = []
            try:
                while True:
                    line = input(">>> " if not code_lines else "... ")
                    if line.strip() == 'EOF':
                        break
                    code_lines.append(line)
            except EOFError:
                pass
            
            code = '\n'.join(code_lines)
        
        if not code.strip():
            return "No code provided"
        
        print(f"Running {language} code...")
        stdout, stderr, returncode = self.code_runner.run_code(code, language)
        
        result = []
        if stdout:
            result.append(f"📤 Output:\n{stdout}")
        if stderr:
            result.append(f"❌ Error:\n{stderr}")
        if returncode != 0:
            result.append(f"Return code: {returncode}")
        
        return '\n\n'.join(result) if result else "Code executed successfully (no output)"
    
    def handle_improve_command(self, args: List[str]) -> str:
        """Handle code improvement command"""
        if not args:
            return "Usage: /improve <file_path> [language]"
        
        file_path = args[0]
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"
        
        # Detect language from file extension if not provided
        language = None
        if len(args) > 1:
            language = args[1].lower()
        else:
            ext = Path(file_path).suffix.lower()
            ext_to_lang = {'.py': 'python', '.js': 'javascript', '.java': 'java', 
                          '.cpp': 'cpp', '.c': 'c', '.go': 'go', '.rs': 'rust'}
            language = ext_to_lang.get(ext, 'unknown')
        
        with open(file_path, 'r') as f:
            code = f.read()
        
        suggestions = self.ai_assistant.analyze_code(code, language)
        return f"📋 Code Analysis for {file_path}:\n\n{suggestions}"
    
    def handle_explain_command(self, code: str) -> str:
        """Handle code explanation command"""
        # This would integrate with AI to explain code
        return f"🧠 Code Explanation:\n\nThis code appears to implement functionality in the given programming language. For detailed explanation, I would analyze the code structure, logic flow, and purpose of each component.\n\n(Note: Connect to AI API for detailed explanations)"
    
    def interactive_mode(self):
        """Start interactive chat mode"""
        self.print_banner()
        
        print("Type '/help' for commands, '/exit' to quit, or just start chatting!\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    command_parts = user_input[1:].split()
                    command = command_parts[0].lower()
                    args = command_parts[1:]
                    
                    if command == 'exit' or command == 'quit':
                        print("👋 Goodbye! Happy coding!")
                        break
                    
                    elif command == 'help':
                        response = self.ai_assistant.chat("help")
                        print(f"\nDevBot: {response}\n")
                    
                    elif command == 'run':
                        response = self.handle_run_command(args)
                        print(f"\n{response}\n")
                        self.save_history(user_input, response)
                    
                    elif command == 'improve':
                        response = self.handle_improve_command(args)
                        print(f"\n{response}\n")
                        self.save_history(user_input, response)
                    
                    elif command == 'explain':
                        if args:
                            response = self.handle_explain_command(' '.join(args))
                            print(f"\n{response}\n")
                        else:
                            print("\nUsage: /explain <code_snippet>\n")
                    
                    elif command == 'clear':
                        os.system('clear' if os.name == 'posix' else 'cls')
                    
                    elif command == 'history':
                        if self.history_file.exists():
                            with open(self.history_file, 'r') as f:
                                history = json.load(f)
                            print("\n📚 Recent History:")
                            for entry in history[-10:]:  # Show last 10 entries
                                print(f"[{entry['timestamp'][:19]}] {entry['command']}")
                            print()
                        else:
                            print("\nNo history found.\n")
                    
                    else:
                        print(f"\nUnknown command: {command}\nType '/help' for available commands.\n")
                
                else:
                    # Regular chat
                    response = self.ai_assistant.chat(user_input)
                    print(f"\nDevBot: {response}\n")
                    self.save_history(user_input, response)
            
            except KeyboardInterrupt:
                print("\n\nUse '/exit' to quit gracefully.")
            except EOFError:
                print("\n👋 Goodbye! Happy coding!")
                break

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='DevBot CLI - AI Assistant for Developers')
    parser.add_argument('--run', nargs=2, metavar=('LANG', 'FILE'), 
                       help='Run code file directly')
    parser.add_argument('--improve', nargs=1, metavar='FILE',
                       help='Analyze and improve code file')
    parser.add_argument('--version', action='version', version='DevBot CLI 1.0.0')
    
    args = parser.parse_args()
    
    bot = DevBotCLI()
    
    if args.run:
        language, file_path = args.run
        result = bot.handle_run_command([language, file_path])
        print(result)
    elif args.improve:
        result = bot.handle_improve_command(args.improve)
        print(result)
    else:
        bot.interactive_mode()

if __name__ == '__main__':
    main()