# UMA Calculator 使用手册

## 目录

1. [简介](#简介)
2. [目录结构](#目录结构)
3. [工作原理](#工作原理)
4. [安装配置](#安装配置)
5. [使用说明](#使用说明)
6. [故障排除](#故障排除)

---

## 简介

UMA Calculator 是一个基于 FAIRChem UMA 模型的材料科学计算工具，提供类 VASP 的接口用于运行机器学习势能（MLIP）计算。支持单点能计算、几何优化、分子动力学等多种计算类型。

### 主要特性

- **交互式界面**：提供 TUI（终端用户界面）和 CLI（命令行界面）两种操作方式
- **多种计算类型**：单点能计算（SP）、几何优化（OPT）、分子动力学（MD）
- **智能预优化**：MD 计算前自动进行结构预优化，防止原子飞散
- **VASP 兼容输出**：生成 OUTCAR、CONTCAR、XDATCAR 等标准格式文件

---

## 目录结构

```
uma/
├── uma_calc.py                 # 程序入口
├── setup.py                    # 安装配置
├── uma-s-1.pt                  # UMA Small 模型 (1.1GB)
├── uma-m-1p1.pt                # UMA Medium 模型 (11GB)
│
├── 结构文件/                    # 示例输入文件
│   ├── 1.cif                   # CIF 格式晶体结构
│   ├── POSCAR                  # VASP POSCAR 格式
│   └── CONTCAR                 # 优化后的结构
│
├── umakit/                     # 核心程序包
│   ├── __init__.py
│   ├── calculator.py           # UMA 计算器封装
│   ├── cli.py                  # 命令行接口
│   ├── config.py               # INCAR 配置解析
│   ├── logger.py               # 日志系统
│   ├── utils.py                # 工具函数
│   │
│   ├── runners/                # 计算运行器
│   │   ├── base.py             # 基类
│   │   ├── singlepoint.py      # 单点能计算
│   │   ├── optimization.py     # 几何优化
│   │   ├── md.py               # 分子动力学
│   │   └── batch.py            # 批量处理
│   │
│   ├── tui/                    # TUI 界面
│   │   ├── app.py              # TUI 应用主类
│   │   ├── main_screen.py      # 主菜单
│   │   ├── config_screen.py    # 配置界面
│   │   └── run_screen.py       # 运行界面
│   │
│   └── writers/                # 输出文件写入器
│       ├── outcar.py           # OUTCAR 格式
│       ├── contcar.py          # CONTCAR 格式
│       ├── xdatcar.py          # XDATCAR 格式 (MD轨迹)
│       ├── oszicar.py          # OSZICAR 格式 (优化进度)
│       ├── json_writer.py      # JSON 格式结果
│       └── trajectory.py       # ASE 轨迹
│
├── docs/                       # 文档
│   ├── README_CN.md            # 中文文档 (本文档)
│   ├── README_EN.md            # 英文文档
│   ├── EXAMPLES.md             # 示例
│   └── USER_GUIDE.md           # 用户指南
│
└── templates/                  # INCAR 模板
    ├── INCAR.sp                # 单点能模板
    ├── INCAR.opt               # 几何优化模板
    └── INCAR.md                # 分子动力学模板
```

---

## 工作原理

### 架构概述

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   CLI 命令   │  │   TUI 界面   │  │   INCAR 配置文件     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        计算控制层                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │  SinglePoint │ │ Optimization │ │  Molecular Dynamics  │ │
│  │    Runner    │ │    Runner    │ │       Runner         │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        模型推理层                             │
│              ┌───────────────────────────┐                  │
│              │   FAIRChem UMA Model      │                  │
│              │   (uma-s-1.pt / uma-m-1p1.pt)              │
│              └───────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        输出处理层                             │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐  │
│  │ OUTCAR │ │CONTCAR │ │XDATCAR │ │ JSON   │ │  trajectory│  │
│  └────────┘ └────────┘ └────────┘ └────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 计算流程

1. **结构输入**：读取 CIF、POSCAR、XYZ 等格式的原子结构
2. **模型加载**：加载预训练的 UMA 模型（SO(3) 等变神经网络）
3. **图构建**：构建原子邻居图，考虑周期性边界条件
4. **前向计算**：模型推理得到能量、力、应力
5. **后处理**：根据计算类型进行优化或 MD 积分
6. **结果输出**：生成各种格式的输出文件

### MD 预优化机制

传统的 MD 模拟经常因为初始结构有内部应力而导致原子飞散。本程序在 MD 前自动执行 FIRE 优化：

```python
# 预优化阶段
optimizer = FIRE(atoms, logfile=None)
optimizer.run(fmax=0.1, steps=50)  # 快速消除应力

# 然后再启动 MD
dyn = Langevin(atoms, ...)
dyn.run(steps)
```

---

## 安装配置

### 环境要求

- Python >= 3.10
- CUDA >= 11.8 (如需 GPU 支持)
- 内存 >= 16GB (推荐 32GB)

### 安装步骤

```bash
# 1. 克隆或下载代码
cd /path/to/uma

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install torch>=2.0.0
pip install ase>=3.26.0
pip install fairchem-core
pip install textual  # TUI 界面所需

# 4. 或使用 uv 安装
uv pip install -e .
```

### 模型下载

```bash
# UMA Small 模型 (推荐，1.1GB)
# 下载地址: https://fair-chem.github.io/models/uma/

# UMA Medium 模型 (11GB，更高精度)
```

---

## 使用说明

### 方式一：TUI 交互界面

```bash
# 启动 TUI 界面
python uma_calc.py
```

**操作指南：**

| 按键 | 功能 |
|------|------|
| `↑/↓` | 选择菜单项 |
| `Enter` | 确认选择 |
| `Tab` | 切换到下一个输入框 |
| `Esc` | 返回上一级 |
| `Q` | 退出程序 |
| `↑/↓/PgUp/PgDn` | 滚动页面 |

**使用流程：**

1. **选择计算类型**：SP / OPT / MD / Batch / Template
2. **配置参数**：
   - Structure File: 输入结构文件路径（如 `1.cif`）
   - Model File: 输入模型路径（如 `uma-s-1.pt`）
   - Output Directory: 输出目录（默认 `./results`）
   - Task Type: 选择任务类型（omat/oc20/omol等）
   - Device: CPU 或 CUDA
3. **计算选项**：根据计算类型设置特定参数
4. **点击 Run**：开始计算

### 方式二：CLI 命令行

#### 单点能计算 (SP)

```bash
# 基本用法
python uma_calc.py sp structure.cif --model uma-s-1.pt --task omat

# 指定设备和输出目录
python uma_calc.py sp POSCAR \
    --model uma-s-1.pt \
    --task omat \
    --device cuda \
    --output ./results
```

#### 几何优化 (OPT)

```bash
# 基本优化
python uma_calc.py opt structure.cif --model uma-s-1.pt

# 带晶胞优化的紧收敛
python uma_calc.py opt POSCAR \
    --model uma-s-1.pt \
    --fmax 0.02 \
    --max-steps 1000 \
    --cell-opt \
    --optimizer FIRE
```

**参数说明：**
- `--fmax`: 力收敛阈值 (eV/Å)，默认 0.05
- `--max-steps`: 最大优化步数，默认 500
- `--optimizer`: 优化算法 (FIRE/BFGS/LBFGS)
- `--cell-opt`: 启用晶胞优化
- `--fix-symmetry`: 保持对称性

#### 分子动力学 (MD)

```bash
# NVT 系综 @ 300K
python uma_calc.py md structure.cif \
    --model uma-s-1.pt \
    --ensemble NVT \
    --temp 300 \
    --steps 10000 \
    --timestep 1.0

# NVE 系综
python uma_calc.py md POSCAR \
    --model uma-s-1.pt \
    --ensemble NVE \
    --temp 300 \
    --steps 5000
```

**参数说明：**
- `--ensemble`: 系综类型 (NVT/NVE)
- `--temp`: 温度 (K)，默认 300
- `--timestep`: 时间步长 (fs)，默认 1.0
- `--steps`: 模拟步数，默认 1000
- `--save-interval`: 保存间隔，默认 10

**注意：** MD 会自动进行预优化以消除应力。

#### 批量处理 (Batch)

```bash
# 批量单点能计算
python uma_calc.py batch structures/ \
    --model uma-s-1.pt \
    --calc-type sp \
    --pattern "*.cif" \
    --output batch_results
```

#### 生成模板

```bash
# 生成 INCAR 模板
python uma_calc.py template sp -o INCAR.sp
python uma_calc.py template opt -o INCAR.opt
python uma_calc.py template md -o INCAR.md
```

#### INCAR 文件运行

```bash
# 从 INCAR 文件运行
python uma_calc.py run -i INCAR.uma -s structure.cif -o results/
```

**INCAR 文件示例：**

```bash
# INCAR.uma - 几何优化配置
CALC_TYPE = OPT
TASK = omat
MODEL_PATH = uma-s-1.pt
DEVICE = cuda

OPT_ALGO = FIRE
FMAX = 0.05
MAX_STEPS = 500
CELL_OPT = .TRUE.
```

---

## 输出文件

### 标准输出

| 文件 | 说明 |
|------|------|
| `OUTCAR` | VASP 格式详细输出，包含能量、力、应力 |
| `CONTCAR` | 最终/优化后的结构 |
| `uma_results.json` | JSON 格式结果，便于程序读取 |
| `calculation.log` | 计算日志 |

### MD 特有输出

| 文件 | 说明 |
|------|------|
| `XDATCAR` | MD 轨迹（VASP 格式）|
| `trajectory.traj` | ASE 轨迹文件 |

### 优化特有输出

| 文件 | 说明 |
|------|------|
| `OSZICAR` | 优化进度日志 |
| `optimization.log` | ASE 优化器日志 |

---

## 任务类型说明

| 任务 | 适用体系 | 电荷/自旋 | 应力 | 用途 |
|------|----------|-----------|------|------|
| `omat` | 无机材料 | 可选 | ✓ | 体相材料、电池材料 |
| `omol` | 分子 | **必须** | ✗ | 有机分子、化学反应 |
| `oc20` | 催化表面 | 可选 | ✓ | 表面吸附、催化 |
| `oc25` | 催化（扩展） | 可选 | ✓ | 扩展催化数据集 |
| `odac` | MOFs | 可选 | ✓ | 金属有机框架 |
| `omc` | 分子晶体 | 可选 | ✓ | 有机晶体 |

**分子计算注意事项：**

对于 `omol` 任务，必须在结构文件中指定电荷和自旋：

```python
from ase.io import read, write

atoms = read("molecule.xyz")
atoms.info["charge"] = 0   # 总电荷
atoms.info["spin"] = 1     # 自旋多重度 (2S+1)
write("molecule_with_charge.xyz", atoms)
```

---

## 故障排除

### 常见问题

#### 1. MD 计算原子飞散

**现象：** MD 运行几步后报错 "No edges found"

**解决：**
- 程序已内置预优化，通常无需处理
- 如仍有问题，先运行 OPT 优化结构
- 降低初始温度：`--temp 100`

```bash
# 先优化
python uma_calc.py opt structure.cif --model uma-s-1.pt --max-steps 100
# 再用优化后的结构跑 MD
python uma_calc.py md CONTCAR --model uma-s-1.pt --temp 100
```

#### 2. CUDA 内存不足

**现象：** `RuntimeError: CUDA out of memory`

**解决：**
- 使用 CPU 计算：`--device cpu`
- 使用更小的模型：`uma-s-1.pt` 替代 `uma-m-1p1.pt`
- 减小 batch size（当前版本自动处理）

#### 3. TUI 界面无法输入

**现象：** 输入框无法获得焦点

**解决：**
- 使用 `Tab` 键切换焦点
- 确保终端窗口足够大（建议至少 80x24）
- 使用方向键或 PgUp/PgDn 滚动页面

#### 4. 结构文件读取失败

**现象：** `Error reading structure`

**解决：**
- 检查文件格式（CIF、POSCAR、XYZ 等）
- 检查文件编码（应为 UTF-8）
- 尝试用 ASE 直接读取测试：

```python
from ase.io import read
try:
    atoms = read("structure.cif")
    print(f"Success: {atoms}")
except Exception as e:
    print(f"Error: {e}")
```

---

## 性能优化建议

### GPU 加速

```bash
# 使用 CUDA 设备
python uma_calc.py sp structure.cif --model uma-s-1.pt --device cuda

# 对于 MD，自动使用 turbo 模式
python uma_calc.py md structure.cif --model uma-s-1.pt --device cuda
```

### 批量计算

```bash
# 使用 batch 模式处理多个结构
python uma_calc.py batch structures/ \
    --model uma-s-1.pt \
    --calc-type sp \
    --pattern "*.cif"
```

---

## 联系我们

如有问题或建议，请通过以下方式联系：

- GitHub Issues: [fairchem](https://github.com/FAIR-Chem/fairchem)
- 文档: [fair-chem.github.io](https://fair-chem.github.io)

---

## 许可证

本项目基于 MIT 许可证开源。

Copyright (c) Meta Platforms, Inc. and affiliates.
