#!/usr/bin/env python3
"""
Script to compile .proto files to Python
"""
import subprocess
import os
import sys

def compile_proto(service_dir, proto_files):
    """Compile proto files in a service directory"""
    proto_path = os.path.join(service_dir, 'proto')
    
    if not os.path.exists(proto_path):
        print(f"Proto directory not found: {proto_path}")
        return False
    
    # Build the command
    cmd = [
        'python', '-m', 'grpc_tools.protoc',
        f'-I{proto_path}',
        f'--python_out={proto_path}',
        f'--grpc_python_out={proto_path}'
    ]
    
    # Add all proto files
    for proto_file in proto_files:
        cmd.append(os.path.join(proto_path, proto_file))
    
    print(f"\nCompiling proto files in {service_dir}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ Compiled successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error compiling proto files")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main function"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    services = {
        os.path.join(base_dir, 'service_a'): ['user.proto'],
        os.path.join(base_dir, 'service_b'): ['product.proto', 'user.proto'],
        os.path.join(base_dir, 'service_c'): ['order.proto', 'user.proto', 'product.proto'],
    }
    
    print("=" * 60)
    print("Proto File Compiler")
    print("=" * 60)
    
    all_success = True
    for service_dir, proto_files in services.items():
        if not compile_proto(service_dir, proto_files):
            all_success = False
    
    # Create __init__.py files in proto directories
    for service_dir in services.keys():
        proto_dir = os.path.join(service_dir, 'proto')
        init_file = os.path.join(proto_dir, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write("")
            print(f"Created {init_file}")
    
    print("\n" + "=" * 60)
    if all_success:
        print("✓ All proto files compiled successfully!")
        return 0
    else:
        print("✗ Some proto files failed to compile")
        return 1

if __name__ == '__main__':
    sys.exit(main())
