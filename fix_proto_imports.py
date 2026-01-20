#!/usr/bin/env python3
"""
Fix import paths in generated proto files
"""
import os
import re

def fix_imports(service_dir, proto_modules):
    """Fix relative imports in generated proto files"""
    proto_path = os.path.join(service_dir, 'proto')
    
    for proto_module in proto_modules:
        # Fix .py imports
        grpc_file = os.path.join(proto_path, f'{proto_module}_pb2_grpc.py')
        pb2_file = os.path.join(proto_path, f'{proto_module}_pb2.py')
        
        if os.path.exists(grpc_file):
            with open(grpc_file, 'r') as f:
                content = f.read()
            
            # Fix imports to be relative
            content = re.sub(
                rf'import {proto_module}_pb2 as',
                f'from . import {proto_module}_pb2 as',
                content
            )
            
            # Fix any other relative imports
            for other_module in proto_modules:
                if other_module != proto_module:
                    content = re.sub(
                        rf'import {other_module}_pb2 as',
                        f'from . import {other_module}_pb2 as',
                        content
                    )
            
            with open(grpc_file, 'w') as f:
                f.write(content)
            print(f"Fixed {grpc_file}")
        
        if os.path.exists(pb2_file):
            with open(pb2_file, 'r') as f:
                content = f.read()
            
            # Fix imports in pb2 file if needed
            for other_module in proto_modules:
                if other_module != proto_module:
                    content = re.sub(
                        rf'import {other_module}_pb2 as',
                        f'from . import {other_module}_pb2 as',
                        content
                    )
            
            with open(pb2_file, 'w') as f:
                f.write(content)
            print(f"Fixed {pb2_file}")

def main():
    """Main function"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    services = {
        os.path.join(base_dir, 'service_a'): ['user'],
        os.path.join(base_dir, 'service_b'): ['product', 'user'],
        os.path.join(base_dir, 'service_c'): ['order', 'user', 'product'],
    }
    
    print("=" * 60)
    print("Fixing Proto Import Paths")
    print("=" * 60)
    
    for service_dir, proto_modules in services.items():
        print(f"\nProcessing {os.path.basename(service_dir)}...")
        fix_imports(service_dir, proto_modules)
    
    print("\n" + "=" * 60)
    print("✓ All imports fixed!")

if __name__ == '__main__':
    main()
