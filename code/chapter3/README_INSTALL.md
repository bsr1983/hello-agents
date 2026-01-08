# Chapter3 依赖安装指南

## 问题说明

如果遇到 `torch` 安装失败的问题，可能是因为 Python 版本过新。

## Python 版本要求

PyTorch 目前支持 Python 3.8-3.12。如果您的 Python 版本是 3.13 或 3.14，可能需要：

1. **使用 Python 3.11 或 3.12**（推荐）
2. 或者等待 PyTorch 更新支持

## 解决方案

### 方案1：使用 Python 3.11 或 3.12（推荐）

```bash
# 创建新的虚拟环境，指定 Python 版本
python3.11 -m venv venv_chapter3
# 或
python3.12 -m venv venv_chapter3

# 激活虚拟环境
source venv_chapter3/bin/activate  # macOS/Linux
# 或
venv_chapter3\Scripts\activate  # Windows

# 安装依赖
pip install -r requestments.txt
```

### 方案2：检查可用的 Python 版本

```bash
# 查看系统中可用的 Python 版本
which python3.11
which python3.12
python3.11 --version
python3.12 --version
```

### 方案3：使用 conda（如果已安装）

```bash
# 创建 Python 3.11 环境
conda create -n chapter3 python=3.11
conda activate chapter3
pip install -r requestments.txt
```

## 依赖说明

- `torch>=2.0.0` - PyTorch 深度学习框架
- `transformers>=4.30.0` - Hugging Face Transformers 库
- `numpy>=1.24.0` - 数值计算库

## 安装命令

```bash
# 标准安装
pip install -r requestments.txt

# 使用国内镜像源（推荐）
pip install -r requestments.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 如果 torch 安装失败，可以单独安装
pip install torch transformers numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 验证安装

```bash
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import transformers; print(f'Transformers version: {transformers.__version__}')"
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
```

