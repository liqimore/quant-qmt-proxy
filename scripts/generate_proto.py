"""
生成 protobuf 代码
"""
import os,sys
import subprocess
from pathlib import Path


def generate_protobuf():
    """生成 protobuf Python 代码"""
    # 项目根目录
    project_root = Path(__file__).parent.parent
    proto_dir = project_root / "proto"
    output_dir = project_root / "generated"
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True)
    
    # 生成 Python 代码
    proto_files = list(proto_dir.glob("*.proto"))
    
    if not proto_files:
        print("❌ 未找到 .proto 文件")
        return
    
    print(f"📝 找到 {len(proto_files)} 个 proto 文件")
    
    for proto_file in proto_files:
        cmd = [
            sys.executable, "-m", "grpc_tools.protoc",
            f"--proto_path={proto_dir}",
            f"--python_out={output_dir}",
            f"--grpc_python_out={output_dir}",
            str(proto_file)
        ]
        
        print(f"生成 {proto_file.name}...")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"  ✅ {proto_file.name} 生成成功")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ {proto_file.name} 生成失败:")
            print(f"     {e.stderr}")
            raise
    
    # 创建 __init__.py
    init_file = output_dir / "__init__.py"
    init_file.touch()
    print(f"\n✅ 创建 {init_file}")
    
    # 修复生成文件中的 import 路径
    print("\n🔧 修复 import 路径...")
    fix_imports(output_dir)
    
    print("\n✅ Protobuf 代码生成完成！")
    print(f"   输出目录: {output_dir}")


def fix_imports(output_dir: Path):
    """修复生成的 Python 文件中的 import 路径"""
    import re
    
    # 修复 _grpc.py 文件中的 import
    grpc_patterns = [
        (r'import data_pb2 as data__pb2', 'from generated import data_pb2 as data__pb2'),
        (r'import trading_pb2 as trading__pb2', 'from generated import trading_pb2 as trading__pb2'),
        (r'import common_pb2 as common__pb2', 'from generated import common_pb2 as common__pb2'),
        (r'import health_pb2 as health__pb2', 'from generated import health_pb2 as health__pb2'),
    ]
    
    for py_file in output_dir.glob("*_grpc.py"):
        print(f"  修复 {py_file.name}...")
        content = py_file.read_text(encoding='utf-8')
        
        for old_pattern, new_pattern in grpc_patterns:
            content = re.sub(old_pattern, new_pattern, content)
        
        py_file.write_text(content, encoding='utf-8')
    
    # 修复 _pb2.py 文件中的 import
    pb2_patterns = [
        (r'^import common_pb2 as common__pb2', 'from generated import common_pb2 as common__pb2'),
        (r'^import trading_pb2 as trading__pb2', 'from generated import trading_pb2 as trading__pb2'),
    ]
    
    for py_file in output_dir.glob("*_pb2.py"):
        if py_file.name == 'common_pb2.py':
            continue  # 跳过 common_pb2.py，它不需要修复
        
        print(f"  修复 {py_file.name}...")
        content = py_file.read_text(encoding='utf-8')
        
        for old_pattern, new_pattern in pb2_patterns:
            content = re.sub(old_pattern, new_pattern, content, flags=re.MULTILINE)
        
        py_file.write_text(content, encoding='utf-8')


if __name__ == '__main__':
    try:
        generate_protobuf()
    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
