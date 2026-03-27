"""
精简版 Protobuf 代码生成器

特性：
- 使用 grpc_tools 的 Python API
- 支持全量生成和增量生成
- 自动修复 import 路径
- 重置（清理）功能
"""

import logging
import sys
import time

from dataclasses import dataclass
from pathlib import Path

# 尝试导入 grpc_tools，如果失败则提供友好的错误信息
try:
    from grpc_tools import protoc
except ImportError as e:
    print("错误: 无法导入 grpc_tools，请确保已安装 grpcio-tools")
    print("安装命令: pip install grpcio-tools")
    print(f"详细错误: {e}")
    sys.exit(1)


def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@dataclass
class ProtoConfig:
    """Protobuf 配置类"""

    proto_dir: Path
    output_dir: Path
    python_package: str = "generated"
    incremental: bool = False  # True为增量生成，False为全量生成


class ProtoGenerator:
    """Protobuf 代码生成器"""

    def __init__(self, config: ProtoConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def reset(self):
        """重置：清理输出目录"""
        if self.config.output_dir.exists():
            self.logger.info(f"清理输出目录: {self.config.output_dir}")

            # 删除所有生成的 Python 文件，保留 __init__.py
            # 修复：分别处理不同的文件扩展名
            for ext in ["*.py", "*.pyi"]:
                for py_file in self.config.output_dir.glob(ext):
                    if py_file.name != "__init__.py":
                        try:
                            py_file.unlink()
                            self.logger.info(
                                f"删除文件: {py_file}"
                            )  # 改为info级别以便更好地调试
                        except Exception as e:
                            self.logger.error(f"删除文件失败: {py_file}, 错误: {e}")

            # 删除子目录（如果有的话）
            for sub_dir in self.config.output_dir.iterdir():
                if sub_dir.is_dir():
                    import shutil

                    shutil.rmtree(sub_dir)
                    self.logger.debug(f"删除目录: {sub_dir}")

    def find_proto_files(self) -> list[Path]:
        """查找所有 .proto 文件"""
        proto_files: list[Path] = list(self.config.proto_dir.glob("*.proto"))
        # 过滤掉非文件类型
        proto_files = [f for f in proto_files if f.is_file()]

        if not proto_files:
            raise FileNotFoundError(f"在 {self.config.proto_dir} 中未找到 .proto 文件")

        self.logger.info(f"找到 {len(proto_files)} 个 proto 文件")
        for proto_file in proto_files:
            self.logger.info(f"  - {proto_file.name}")

        return proto_files

    def should_generate(self, proto_file: Path) -> bool:
        """判断是否需要生成（用于增量生成）"""
        if not self.config.incremental:
            return True  # 全量生成

        # 检查对应的 Python 文件是否存在且比 proto 文件新
        pb2_file: Path = self.config.output_dir / f"{proto_file.stem}_pb2.py"
        grpc_file: Path = self.config.output_dir / f"{proto_file.stem}_pb2_grpc.py"

        if not pb2_file.exists() or not grpc_file.exists():
            return True

        # 比较时间戳
        proto_time: float = proto_file.stat().st_mtime
        pb2_time: float = pb2_file.stat().st_mtime
        grpc_time: float = grpc_file.stat().st_mtime

        return proto_time > pb2_time or proto_time > grpc_time

    def get_protoc_include_path(self) -> Path | None:
        """获取 protoc 的 include 路径"""
        try:
            import site

            import grpc_tools

            # 查找 grpc_tools 安装路径
            grpc_tools_path: Path = Path(grpc_tools.__file__).parent

            # 可能的 include 路径
            possible_paths: list[Path] = [
                grpc_tools_path / "_proto",
                Path(site.getsitepackages()[0]) / "grpc_tools" / "_proto",
                Path("/usr") / "include",
                Path("/usr") / "local" / "include",
            ]

            for p in possible_paths:
                self.logger.info(f"检查路径: {p}")

            for path in possible_paths:
                if path.exists() and (path / "google" / "protobuf").exists():
                    self.logger.debug(f"找到 protoc include 路径: {path}")
                    return path

            self.logger.warning(
                "未找到 protoc include 路径，google/protobuf 导入可能失败"
            )
            return None

        except Exception as e:
            self.logger.warning(f"查找 protoc include 路径失败: {e}")
            return None

    def generate_proto_file(self, proto_file: Path) -> bool:
        """生成单个 proto 文件的代码"""
        # 确保输出目录存在
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        # 构建 protoc 参数
        proto_args: list[str] = [
            f"--proto_path={self.config.proto_dir}",
            f"--python_out={self.config.output_dir}",
            f"--grpc_python_out={self.config.output_dir}",
            f"--pyi_out={self.config.output_dir}",
        ]

        # 添加 protoc include 路径
        include_path: Path | None = self.get_protoc_include_path()
        if include_path:
            proto_args.insert(0, f"--proto_path={include_path}")

        # 添加要编译的 proto 文件
        proto_args.append(str(proto_file))

        # 添加 protoc 命令参数
        command_args: list[str] = ["protoc", *proto_args]

        self.logger.info(f"生成 {proto_file.name}...")

        try:
            # 使用 grpc_tools.protoc 的 main 函数
            result = protoc.main(command_args)

            if result == 0:
                self.logger.info(f"  {proto_file.name} 生成成功")
                return True
            else:
                self.logger.error(f"  {proto_file.name} 生成失败，返回状态: {result}")
                return False

        except Exception as e:
            self.logger.error(f"  {proto_file.name} 生成异常: {e}")
            return False

    def fix_imports(self):
        """修复生成的 Python 文件中的 import 路径"""
        import re

        self.logger.info("修复 import 路径...")

        # 找出项目中所有生成的pb2文件名（从proto文件推导）
        project_pb2_files: list[str] = []
        for proto_file in self.config.proto_dir.glob("*.proto"):
            pb2_name = proto_file.stem + "_pb2"
            project_pb2_files.append(pb2_name)

        # 查找所有生成的 Python 文件
        for py_file in self.config.output_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue

            self.logger.debug(f"  修复 {py_file.name}...")
            content: str = py_file.read_text(encoding="utf-8")
            original_content: str = content

            # 只修复项目自己的pb2文件导入，避免修改google.protobuf相关导入
            for pb2_name in project_pb2_files:
                # 修复 import xxx_pb2 as xxx__pb2 模式
                import_pattern: str = (
                    rf"import {pb2_name} as ({pb2_name.replace('_', '__')})"
                )
                replacement: str = (
                    f"import {self.config.python_package}.{pb2_name} as \\1"
                )
                content = re.sub(import_pattern, replacement, content)

                # 修复 from xxx_pb2 import 模式
                from_pattern: str = rf"from {pb2_name} import"
                replacement = f"from {self.config.python_package}.{pb2_name} import"
                content = re.sub(from_pattern, replacement, content)

            # 如果内容有变化，则写入文件
            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                self.logger.debug(f"    {py_file.name} 修复完成")

    def generate(self) -> bool:
        """执行代码生成流程"""
        try:
            # 查找 proto 文件
            proto_files: list[Path] = self.find_proto_files()

            # 过滤需要生成的文件（增量/全量）
            files_to_generate: list = []
            for proto_file in proto_files:
                if self.should_generate(proto_file):
                    files_to_generate.append(proto_file)
                else:
                    self.logger.info(f"跳过 {proto_file.name} (已存在且为最新)")

            if not files_to_generate:
                self.logger.info("没有需要生成的文件")
                return True

            # 生成代码
            success_count = 0
            for proto_file in files_to_generate:
                if self.generate_proto_file(proto_file):
                    success_count += 1

            if success_count == 0:
                self.logger.error("所有 proto 文件生成失败")
                return False

            # 修复 import 路径
            self.fix_imports()

            self.logger.info(
                f"Protobuf 代码生成完成！成功生成 {success_count}/{len(files_to_generate)} 个文件"
            )
            self.logger.info(f"输出目录: {self.config.output_dir}")

            return True

        except Exception as e:
            self.logger.error(f"代码生成失败: {e}")
            return False


def main():
    """主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)

    import argparse

    parser = argparse.ArgumentParser(description="Protobuf 代码生成器")
    parser.add_argument(
        "--mode",
        choices=["generate", "incremental", "reset"],
        default="incremental",
        help="执行模式: generate(全量生成), incremental(增量生成), reset(重置)",
    )
    parser.add_argument("--proto-dir", default="proto", help="proto文件目录")
    parser.add_argument("--output-dir", default="generated", help="输出目录")
    parser.add_argument("--package", default="generated", help="Python包名")

    args = parser.parse_args()

    try:
        # 配置
        config = ProtoConfig(
            proto_dir=Path(args.proto_dir),
            output_dir=Path(args.output_dir),
            python_package=args.package,
            incremental=(args.mode == "incremental"),
        )

        # 创建生成器
        generator = ProtoGenerator(config)

        generator.get_protoc_include_path()

        start_time = time.time()

        if args.mode == "reset":
            generator.reset()
            logger.info("重置完成")
        else:
            # 如果是全量生成，先重置
            if args.mode == "generate":
                generator.reset()

            success = generator.generate()

            if success:
                logger.info(f"生成完成，耗时: {time.time() - start_time:.2f} 秒")
                return 0
            else:
                logger.error("生成失败")
                return 1

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
