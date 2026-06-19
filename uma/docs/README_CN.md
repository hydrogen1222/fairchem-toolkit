# UMAKit — 用户手册

> **通用材料应用计算器**
> 基于 FAIRChem UMA 机器学习原子间势函数的 VASP 兼容接口

---

## 目录

- [1. 简介](#1-简介)
- [2. 安装](#2-安装)
- [3. 快速开始](#3-快速开始)
- [4. 架构概览](#4-架构概览)
- [5. 计算类型](#5-计算类型)
  - [5.1 单点能计算 (SP)](#51-单点能计算-sp)
  - [5.2 几何优化 (OPT)](#52-几何优化-opt)
  - [5.3 分子动力学 (MD)](#53-分子动力学-md)
  - [5.4 批量处理](#54-批量处理)
- [6. 用户界面](#6-用户界面)
  - [6.1 CLI — 命令行界面](#61-cli--命令行界面)
  - [6.2 TUI — 终端交互界面](#62-tui--终端交互界面)
  - [6.3 Python API](#63-python-api)
- [7. INCAR 配置文件参考](#7-incar-配置文件参考)
- [8. 输出文件参考](#8-输出文件参考)
- [9. 任务类型参考](#9-任务类型参考)
- [10. 后台任务管理](#10-后台任务管理)
- [11. 资源控制](#11-资源控制)
- [12. 故障排除与常见问题](#12-故障排除与常见问题)
- [13. 性能指南](#13-性能指南)
- [14. 使用示例](#14-使用示例)
- [15. 许可证](#15-许可证)

---

## 1. 简介

UMAKit 是一个基于 Meta FAIRChem UMA（通用材料应用）模型的材料科学计算工具。它为运行机器学习原子间势函数（MLIP）计算提供了类似 VASP 的用户体验。

**UMAKit 能够做什么：**

- 计算晶体结构和分子的能量、力和应力
- 优化原子位置和晶胞参数（几何弛豫）
- 运行分子动力学模拟（NVT / NVE 系综）
- 批量处理数百个结构
- 以 VASP 兼容格式输出结果（OUTCAR、CONTCAR、XDATCAR、OSZICAR）

**工作原理：**

与 VASP 自洽求解 Kohn-Sham 方程不同，UMAKit 使用预训练的等变神经网络（SO(3) 等变 eSCN 架构）在单次前向传播中预测能量和力。没有电子步，没有 SCF 循环，也没有 k 点。计算成本大致与原子数成线性关系。

```
                          ┌──────────────────┐
  structure.cif  ────────▶│  UMA 神经网络     │───────▶  能量、力、应力
  (原子坐标)              │  (预训练模型)     │         (单次前向传播)
                          └──────────────────┘
```

**核心特性一览：**

| 特性 | 说明 |
|------|------|
| CLI 模式 | 完整的命令行界面，10 个子命令 |
| TUI 模式 | 交互式终端界面，实时进度显示 |
| Python API | 面向脚本和工作流的编程接口 |
| 后台任务 | 提交、分离、重连、终止长时间计算 |
| 批量处理 | 并行处理大量结构 |
| CPU & CUDA | 支持 CPU 和 GPU，自动检测 |
| VASP 输出 | OUTCAR、CONTCAR、XDATCAR、OSZICAR 格式 |
| 跨平台 | Windows、Linux、macOS |

---

## 2. 安装

### 2.1 环境要求

| 需求 | 最低配置 | 推荐配置 |
|------|----------|----------|
| Python | 3.9+ | 3.11+ |
| 内存 | 8 GB | 32 GB |
| 磁盘 | 2 GB（模型：1.2 GB） | 15 GB（更大模型） |
| GPU（可选） | CUDA 11.8+ | CUDA 12.x，8+ GB 显存 |

### 2.2 使用 uv 安装（推荐）

> **重要：** `fairchem-core` 未发布到 PyPI，必须从本仓库的 `packages/fairchem-core/` 目录安装。

```bash
# 克隆仓库
git clone https://github.com/FAIR-Chem/fairchem.git
cd fairchem

# 第 1 步：安装 fairchem-core（必需——必须先完成）
cd packages/fairchem-core
uv pip install -e ".[dev]"

# 第 2 步：安装 UMAKit
cd ../../uma
uv pip install -e .
```

### 2.3 CUDA GPU 与 CPU 安装

UMAKit 不自带 PyTorch——它使用 `fairchem-core` 提供的 PyTorch。

| 场景 | PyTorch | UMAKit 设备参数 |
|------|---------|-----------------|
| **CUDA GPU 机器** | 在 CUDA Python 环境中安装 fairchem-core | `--device cuda` |
| **纯 CPU 机器** | 在标准 Python 环境中安装 fairchem-core | `--device cpu`（默认） |

**安装后验证 CUDA：**

```bash
uv run python -c "import torch; print('CUDA 可用' if torch.cuda.is_available() else '仅 CPU')"
```

**如果有 GPU 但 CUDA 不可用：**
- 确保 PyTorch 构建包含 CUDA（使用 CUDA 索引安装 `pip install torch`）
- 或在已有 CUDA PyTorch 的 conda/venv 环境中安装 `fairchem-core`

### 2.4 如何运行命令

两种等价方式：

```bash
# 方式 A：uv run（推荐——自动检测 .venv，跨平台通用）
uv run uma_calc --help
uv run uma_calc tui
uv run uma_calc sp structure.cif --model uma-s-1.pt

# 方式 B：先激活 venv
source .venv/bin/activate      # Linux/Mac
# .venv\Scripts\activate       # Windows
uma_calc --help
uma_calc tui
```

### 2.5 模型检查点

从 FAIRChem 下载 UMA 模型检查点：

```bash
# UMA Small（推荐入门，约 1.2 GB）
# 下载地址：https://fair-chem.github.io/models/uma/
# 将 .pt 文件放在工作目录或已知路径下
```

模型路径通过 `--model`（CLI）、TUI 配置界面或 INCAR 文件中的 `MODEL_PATH` 键指定。

### 2.6 验证安装

```bash
uv run uma_calc --help
```

应打印帮助信息，显示所有可用的子命令：`sp`、`opt`、`md`、`batch`、`run`、`template`、`jobs`、`kill`、`clean`、`tui`。

---

## 3. 快速开始

### 3.1 第一次计算（CLI）

```bash
# 晶体结构的单点能计算
uv run uma_calc sp structure.cif --model uma-s-1.pt --task omat

# 输出：
# ================================================================================
#                             UMA CALCULATOR
#                (Universal Material Application - FAIRChem)
# ================================================================================
#
# Reading structure from: structure.cif
# System: Li3PS4
# Atoms: 28
#
# Loading model: uma-s-1.pt
#   Calculating energy and forces...
#   Energy: -123.456789 eV
#   Calculation completed in 2.34 s
#
# ================================================================================
#  SUMMARY
# ================================================================================
# Total energy:       -123.45678900 eV
# Energy per atom:      -4.40917068 eV/atom
# Max force:             0.12345678 eV/Å
# RMS force:             0.05678901 eV/Å
# ================================================================================
```

### 3.2 第一次计算（TUI）

```bash
# 启动交互式终端界面
uv run uma_calc tui
```

使用方向键导航，Tab 切换输入字段，Enter 确认选择。

```
┌─ UMA Calculator ───────────────────────────────────────────────────────────────┐
│ Select Calculation Type                                                        │
│                                                                                │
│   Single Point (SP)                                                            │
│     计算能量、力和应力                                                         │
│                                                                                │
│   Geometry Optimization (OPT)                                                  │
│     优化原子位置                                                               │
│                                                                                │
│   Molecular Dynamics (MD)                                                      │
│     运行 NVT/NVE 模拟                                                          │
│                                                                                │
│   Batch Processing                                                             │
│     处理多个结构                                                               │
│                                                                                │
│   Background Jobs                                                              │
│     查看/管理运行中的计算                                                      │
│                                                                                │
│   Generate Template                                                            │
│     创建 INCAR 模板文件                                                        │
│                                                                                │
│   Exit                                                                         │
│     退出程序                                                                   │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 使用 INCAR 文件（VASP 风格）

```bash
# 生成模板
uma_calc template sp -o INCAR.uma

# 编辑：
#   CALC_TYPE = SP
#   TASK = omat
#   MODEL_PATH = uma-s-1.pt
#   DEVICE = cpu

# 从 INCAR 运行
uma_calc run
```

---

## 4. 架构概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                        用户界面层                                    │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐          │
│  │ CLI      │    │ TUI          │    │ Python API       │          │
│  │ (argparse)│   │ (Textual)    │    │ (umakit.api)     │          │
│  └────┬─────┘    └──────┬───────┘    └────────┬─────────┘          │
│       │                 │                     │                     │
│       └─────────────────┼─────────────────────┘                     │
│                         ▼                                           │
│              ┌─────────────────────┐                                │
│              │   EngineConfig      │  ← 统一配置                    │
│              │   (dataclass)       │                                │
│              └─────────┬───────────┘                                │
│                        ▼                                            │
│              ┌─────────────────────┐                                │
│              │ CalculationEngine   │  ← 唯一执行入口                │
│              │ .run() / .run_async()│                               │
│              └─────────┬───────────┘                                │
└────────────────────────┼────────────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────────────┐
│              计算层                                                  │
│              ┌─────────────────────┐                                │
│              │   BaseRunner        │  ← 进度事件、日志              │
│              └─────────┬───────────┘                                │
│         ┌──────────────┼──────────────────┐                         │
│         ▼              ▼                  ▼                          │
│  ┌────────────┐ ┌────────────┐ ┌──────────────┐                     │
│  │SinglePoint │ │Optimization│ │Molecular     │                     │
│  │Runner      │ │Runner      │ │DynamicsRunner│                     │
│  └─────┬──────┘ └─────┬──────┘ └──────┬───────┘                     │
│        │              │               │                              │
│        └──────────────┼───────────────┘                              │
│                       ▼                                              │
│              ┌─────────────────────┐                                │
│              │   UMACalculator     │  ← 封装 FAIRChem ASE 计算器    │
│              └─────────┬───────────┘                                │
└────────────────────────┼────────────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────────────┐
│              模型层                                                  │
│              ┌─────────────────────┐                                │
│              │  FAIRChem UMA 模型  │  ← SO(3) 等变神经网络          │
│              │  InferenceSettings  │     tf32, compile, threads     │
│              └─────────────────────┘                                │
└─────────────────────────────────────────────────────────────────────┘
```

`CalculationEngine` 是核心编排器：所有三种界面（CLI、TUI、API）都构建一个 `EngineConfig` 并调用相同的 `CalculationEngine` 方法。这消除了代码重复，确保行为一致。

---

## 5. 计算类型

### 5.1 单点能计算 (SP)

单点计算针对固定的原子构型计算势能、原子力和（如支持）应力张量。这是最简单、最快的计算类型。

**产生的数据：**
- 总能量 (eV)
- 每个原子的能量 (eV/atom)
- 每个原子上的力 (eV/Å)，包括最大力和均方根力
- 应力张量（Voigt 表示，eV/Å³）—— 如果模型/任务支持
- 压力 (GPa) —— 从应力迹导出

**CLI 用法：**

```bash
uma_calc sp <structure> --model <model.pt> [选项]

# 基本用法
uma_calc sp POSCAR --model uma-s-1.pt --task omat

# 指定输出目录和任务名称
uma_calc sp structure.cif \
    --model uma-s-1.pt \
    --task omat \
    --device cuda \
    --output ./results \
    --name my_calculation
```

**输出文件：** `OUTCAR`、`CONTCAR`、`uma_results.json`

### 5.2 几何优化 (OPT)

优化原子位置（以及可选的晶胞参数）以找到局部能量极小值。当任意原子上的最大力低于收敛阈值（`fmax`）或达到最大步数时计算停止。

**算法：**

| 优化器 | 描述 | 最适用于 |
|--------|------|----------|
| `FIRE` | 快速惯性弛豫引擎（默认） | 大多数体系，稳健 |
| `BFGS` | Broyden-Fletcher-Goldfarb-Shanno | 小体系，快速收敛 |
| `LBFGS` | 有限内存 BFGS | 大体系 |

**CLI 用法：**

```bash
uma_calc opt <structure> --model <model.pt> [选项]

# 基本优化
uma_calc opt POSCAR --model uma-s-1.pt

# 严格收敛 + 晶胞弛豫
uma_calc opt POSCAR \
    --model uma-s-1.pt \
    --fmax 0.02 \
    --max-steps 1000 \
    --cell-opt \
    --optimizer BFGS

# 保持晶体对称性
uma_calc opt structure.cif \
    --model uma-s-1.pt \
    --fix-symmetry
```

**参数：**

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `--fmax` | 0.05 | 力收敛阈值 (eV/Å) |
| `--max-steps` | 500 | 最大优化步数 |
| `--optimizer` | FIRE | FIRE / BFGS / LBFGS |
| `--cell-opt` | 关 | 启用晶胞参数优化 |
| `--fix-symmetry` | 关 | 保持晶体对称性 |

**输出文件：** `OUTCAR`、`CONTCAR`（优化后的结构）、`OSZICAR`（逐步进度）、`uma_results.json`

### 5.3 分子动力学 (MD)

模拟原子在给定温度下的时间演化。支持两种系综：

| 系综 | 积分器 | 描述 |
|------|--------|------|
| NVT | Langevin | 恒粒子数、体积、温度（正则系综） |
| NVE | Velocity Verlet | 恒粒子数、体积、能量（微正则系综） |

**预弛豫：** 在开始 MD 之前，UMAKit 会自动执行快速的 FIRE 优化（默认：50 步，fmax=0.1 eV/Å）以消除内应力。这可以防止"原子爆炸"——由高初始力导致原子飞散的常见失败模式。

**CLI 用法：**

```bash
uma_calc md <structure> --model <model.pt> [选项]

# 300K 下运行 10 ps NVT
uma_calc md POSCAR \
    --model uma-s-1.pt \
    --ensemble NVT \
    --temp 300 \
    --timestep 1.0 \
    --steps 10000 \
    --save-interval 10

# NVE 系综
uma_calc md CONTCAR \
    --model uma-s-1.pt \
    --ensemble NVE \
    --temp 300 \
    --steps 5000
```

**参数：**

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `--ensemble` | NVT | NVT 或 NVE |
| `--temp` | 300 | 温度 (K) |
| `--timestep` | 1.0 | 时间步长 (fs) |
| `--steps` | 1000 | MD 步数 |
| `--friction` | 0.001 | 摩擦系数（仅 NVT，fs⁻¹） |
| `--save-interval` | 10 | 每隔 N 步保存轨迹 |

**输出文件：** `OUTCAR`、`CONTCAR`（最终结构）、`XDATCAR`（轨迹）、`trajectory.traj`（ASE 格式）、`uma_results.json`

### 5.4 批量处理

对目录中的多个结构运行相同类型的计算。支持 `sp` 和 `opt` 计算类型。可通过 `--parallel` 启用并行执行。

**CLI 用法：**

```bash
uma_calc batch <input_dir> --model <model.pt> [选项]

# 对所有 CIF 文件进行 SP 计算
uma_calc batch structures/ \
    --model uma-s-1.pt \
    --calc-type sp \
    --pattern "*.cif" \
    --output batch_results

# 并行对所有 POSCAR 文件进行 OPT
uma_calc batch poscars/ \
    --model uma-s-1.pt \
    --calc-type opt \
    --pattern "POSCAR*" \
    --parallel \
    --workers 4
```

**输出：** 每个结构在输出目录下获得自己的子目录。`batch_summary.json` 文件列出所有结果。

---

## 6. 用户界面

### 6.1 CLI — 命令行界面

CLI 通过 `uma_calc <command> [选项]` 调用。不带参数运行 `uma_calc` 默认启动 TUI。

#### 完整命令参考

##### `uma_calc sp` — 单点能

```
uma_calc sp STRUCTURE --model MODEL [--task TASK] [--device DEVICE]
                       [--output DIR] [--name NAME]

  STRUCTURE             输入结构文件（CIF, XYZ, POSCAR, VASP 等）
  --model MODEL         模型检查点路径（.pt 文件）[必需]
  --task TASK           任务类型：omat|omol|oc20|oc25|odac|omc [默认: omat]
  --device DEVICE       cpu|cuda [默认: cpu]
  --output DIR, -o DIR  输出目录 [默认: .]
  --name NAME, -n NAME  任务名称（输出至 DIR/NAME）
```

##### `uma_calc opt` — 几何优化

```
uma_calc opt STRUCTURE --model MODEL [选项]

  --fmax FMAX           力收敛阈值 eV/Å [默认: 0.05]
  --max-steps N         最大优化步数 [默认: 500]
  --optimizer ALGO      优化算法：FIRE|BFGS|LBFGS [默认: FIRE]
  --cell-opt            启用晶胞参数优化
  --fix-symmetry        保持晶体对称性
```

##### `uma_calc md` — 分子动力学

```
uma_calc md STRUCTURE --model MODEL [选项]

  --ensemble ENSEMBLE   系综：NVT|NVE [默认: NVT]
  --temp TEMP           温度 (K) [默认: 300]
  --timestep DT         时间步长 (fs) [默认: 1.0]
  --steps N             MD 步数 [默认: 1000]
  --friction FRICTION   摩擦系数（NVT）[默认: 0.001]
  --save-interval N     轨迹保存间隔 [默认: 10]
```

##### `uma_calc batch` — 批量处理

```
uma_calc batch INPUT_DIR --model MODEL [选项]

  --calc-type TYPE      计算类型：sp|opt [默认: sp]
  --pattern PATTERN     文件匹配模式 [默认: *.cif]
  --output DIR          输出目录 [默认: batch_results]
```

##### `uma_calc run` — 从 INCAR 文件运行

```
uma_calc run [-i INCAR] [-s STRUCTURE] [-o OUTPUT]

  -i, --incar INCAR     INCAR 文件路径 [默认: INCAR.uma]
  -s, --structure FILE  结构文件（自动检测：POSCAR, CONTCAR, *.cif, *.xyz）
  -o, --output DIR      输出目录 [默认: .]
```

##### `uma_calc template` — 生成 INCAR 模板

```
uma_calc template TYPE [-o OUTPUT]

  TYPE                  sp|opt|md
  -o, --output FILE     输出文件名 [默认: INCAR.<type>]
```

##### `uma_calc jobs` — 列出后台任务

```
uma_calc jobs
```

显示所有后台任务及其 ID、状态、类型、化学式和设备。

##### `uma_calc kill` — 终止后台任务

```
uma_calc kill JOB_ID
```

终止指定任务（跨平台：Windows 使用 `taskkill`，Unix 使用 `SIGTERM`）。

##### `uma_calc clean` — 清理已完成/失败的任务

```
uma_calc clean
```

删除已完成、失败或取消的任务的状态文件。保留正在运行的任务。

##### `uma_calc tui` — 启动 TUI

```
uma_calc tui
```

启动交互式终端用户界面。

### 6.2 TUI — 终端交互界面

TUI 基于 [Textual](https://textual.textualize.io/) 构建，提供交互式、键盘驱动的体验。

#### 导航

| 按键 | 操作 |
|------|------|
| `↑` / `↓` | 导航菜单项 / 滚动 |
| `Tab` | 移至下一个输入字段 |
| `Shift+Tab` | 移至上一个输入字段 |
| `Enter` | 选择 / 确认 |
| `Esc` | 返回上一屏幕 |
| `Q` | 退出程序 |
| `PgUp` / `PgDn` | 可滚动区域的上下翻页 |
| `C` | 取消选中的任务（Jobs 屏幕） |
| `D` | 删除任务记录（Jobs 屏幕） |
| `R` | 刷新任务列表（Jobs 屏幕） |

#### 屏幕说明

**主菜单**（Main Menu）— 选择计算类型（SP、OPT、MD、Batch、Jobs、Template、Exit）。

**配置界面**（Configuration）— 填写路径、任务类型、设备和计算特定参数。路径支持实时验证和视觉反馈：

```
📁 Structure File: [structure.cif                ]
   ✅ Found: /home/user/fairchem/uma/structure.cif
   💡 提示：支持相对路径（例如：./data/structure.cif）
```

**运行界面**（Run）— 显示实时进度：
- SP 计算使用不确定进度条（indeterminate spinner）
- OPT 显示步数计数器（Step 5/500）
- MD 显示步数 + 温度 + 能量

**任务管理**（Jobs）— 使用 DataTable 列出所有后台任务及状态图标：
- ● 运行中 | ✓ 已完成 | ✗ 失败 | ⊘ 已取消
- 按 Enter 查看任务日志输出
- 每 2 秒自动刷新

### 6.3 Python API

用于脚本编写和工作流集成，导入 `umakit.api`：

```python
from umakit.api import run_single_point, run_optimization, run_md
from umakit.api import calculate_energy, calculate_adsorption_energy

# 单点能
results = run_single_point(
    structure="structure.cif",
    model_path="uma-s-1.pt",
    task="omat",
    device="cuda",
    job_name="my_calc",
)
print(f"能量: {results['energy']:.4f} eV")
print(f"力: {results['forces']}")

# 几何优化
results = run_optimization(
    structure="POSCAR",
    model_path="uma-s-1.pt",
    fmax=0.02,
    cell_opt=True,
)
print(f"收敛: {results['converged']}，步数: {results['nsteps']}")

# 分子动力学
results = run_md(
    structure="CONTCAR",
    model_path="uma-s-1.pt",
    ensemble="NVT",
    temperature=300,
    steps=10000,
    save_interval=10,
)
print(f"最终温度: {results['temperature']:.1f} K")

# 快速能量计算
energy = calculate_energy("structure.cif", "uma-s-1.pt")
print(f"能量: {energy:.4f} eV")

# 吸附能
ads_results = calculate_adsorption_energy(
    adsorbed_structure="adsorbed.cif",
    gas_structure="co2.xyz",
    surface_structure="slab.cif",
    model_path="uma-s-1.pt",
    task="oc20",
)
print(f"吸附能: {ads_results['adsorption_energy']:.4f} eV")
```

完整 API 参考：

| 函数 | 返回值 | 描述 |
|------|--------|------|
| `run_single_point(structure, model_path, ...)` | `dict` | SP 能量、力、应力 |
| `run_optimization(structure, model_path, ...)` | `dict` | OPT 含收敛信息 |
| `run_md(structure, model_path, ...)` | `dict` | MD 含轨迹和温度 |
| `calculate_energy(structure, model_path, ...)` | `float` | 快速获取能量值 |
| `calculate_adsorption_energy(ads, gas, surf, ...)` | `dict` | E吸附 = E吸附体系 - E气体 - E表面 |

---

## 7. INCAR 配置文件参考

INCAR 文件采用 VASP 风格的 `KEY = VALUE` 格式。以 `#` 或 `!` 开头的行是注释。

### 7.1 所有 INCAR 关键字

#### 计算控制

| 键 | 类型 | 默认值 | 描述 |
|-----|------|--------|------|
| `CALC_TYPE` | 字符串 | `SP` | 计算类型：`SP`、`OPT`、`MD`、`BATCH` |

#### 模型设置

| 键 | 类型 | 默认值 | 描述 |
|-----|------|--------|------|
| `MODEL_PATH` | 字符串 | `uma-s-1.pt` | 模型检查点路径（.pt 文件） |
| `TASK` | 字符串 | `omat` | 任务类型：`omat`、`omol`、`oc20`、`oc25`、`odac`、`omc` |
| `DEVICE` | 字符串 | `cpu` | 计算设备：`cpu`、`cuda` |
| `INFERENCE_MODE` | 字符串 | `default` | 推理模式：`default`、`turbo` |

#### 输出控制

| 键 | 类型 | 默认值 | 描述 |
|-----|------|--------|------|
| `WRITE_FORCES` | 布尔 | `.TRUE.` | 写入力到 OUTCAR |
| `WRITE_STRESS` | 布尔 | `.TRUE.` | 写入应力到 OUTCAR |
| `WRITE_TRAJECTORY` | 布尔 | `.TRUE.` | MD 写入轨迹 |
| `OUTPUT_FORMAT` | 字符串 | `VASP` | 输出格式：`VASP` |

#### 优化设置

| 键 | 类型 | 默认值 | 描述 |
|-----|------|--------|------|
| `OPT_ALGO` | 字符串 | `FIRE` | 优化器：`FIRE`、`BFGS`、`LBFGS` |
| `FMAX` | 浮点数 | `0.05` | 力收敛阈值 (eV/Å) |
| `MAX_STEPS` | 整数 | `500` | 最大优化步数 |
| `CELL_OPT` | 布尔 | `.FALSE.` | 优化晶胞参数 |
| `FIX_SYMMETRY` | 布尔 | `.FALSE.` | 保持对称性 |

#### MD 设置

| 键 | 类型 | 默认值 | 描述 |
|-----|------|--------|------|
| `MD_ENSEMBLE` | 字符串 | `NVT` | 系综：`NVT`、`NVE` |
| `TEMPERATURE` | 浮点数 | `300.0` | 温度 (K) |
| `TIMESTEP` | 浮点数 | `1.0` | 时间步长 (fs) |
| `STEPS` | 整数 | `10000` | MD 步数 |
| `FRICTION` | 浮点数 | `0.001` | 摩擦系数 |
| `SAVE_INTERVAL` | 整数 | `10` | 轨迹保存间隔 |

### 7.2 模板示例

**INCAR.sp**（单点能）：
```bash
CALC_TYPE = SP
TASK = omat
MODEL_PATH = uma-s-1.pt
DEVICE = cpu
INFERENCE_MODE = default
WRITE_FORCES = .TRUE.
WRITE_STRESS = .TRUE.
```

**INCAR.opt**（几何优化）：
```bash
CALC_TYPE = OPT
TASK = omat
MODEL_PATH = uma-s-1.pt
DEVICE = cuda
OPT_ALGO = FIRE
FMAX = 0.05
MAX_STEPS = 500
CELL_OPT = .FALSE.
FIX_SYMMETRY = .FALSE.
```

**INCAR.md**（分子动力学）：
```bash
CALC_TYPE = MD
TASK = omat
MODEL_PATH = uma-s-1.pt
DEVICE = cuda
INFERENCE_MODE = turbo
MD_ENSEMBLE = NVT
TEMPERATURE = 300.0
TIMESTEP = 1.0
STEPS = 10000
FRICTION = 0.001
SAVE_INTERVAL = 10
```

### 7.3 布尔值

以下均被识别为 `TRUE` 和 `FALSE`（不区分大小写）：

- **TRUE**：`.TRUE.`、`.T.`、`TRUE`、`T`、`YES`、`Y`、`1`
- **FALSE**：`.FALSE.`、`.F.`、`FALSE`、`F`、`NO`、`N`、`0`

---

## 8. 输出文件参考

### 8.1 文件清单

| 文件 | 生成者 | 格式 | 描述 |
|------|--------|------|------|
| `OUTCAR` | SP, OPT, MD | 文本 | VASP 风格详细输出，含能量、力、应力、耗时 |
| `CONTCAR` | SP, OPT, MD | 文本 | 当前/最终原子结构（VASP POSCAR 格式） |
| `OSZICAR` | OPT | 文本 | 逐步优化进度，含能量和力 |
| `XDATCAR` | MD | 文本 | VASP 格式轨迹（串联 POSCAR） |
| `uma_results.json` | SP, OPT, MD | JSON | 机器可读结果，含所有计算量 |
| `trajectory.traj` | MD | 二进制 | ASE 轨迹文件，用于分析 |
| `optimization.log` | OPT | 文本 | ASE 优化器日志 |
| `calculation.log` | 所有 | 文本 | 结构化计算日志 |
| `batch_summary.json` | BATCH | JSON | 批量处理所有结果的汇总 |

### 8.2 OUTCAR 格式

OUTCAR 文件包含以下部分：

```
================================================================================
                         UMA CALCULATION RESULTS
================================================================================

--------------------------------------------------------------------------------
 SYSTEM INFORMATION          ← 体系信息（化学式、原子数、元素种类）
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
 MODEL INFORMATION           ← 模型信息（路径、设备、推理模式、支持属性）
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
 INPUT STRUCTURE             ← 输入结构（晶格矢量、原子位置）
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
 ENERGY                      ← 能量（总能量、每原子能量）
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
 FORCES (eV/Å)              ← 力（每个原子的力分量、最大力、RMS 力）
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
 STRESS TENSOR               ← 应力张量（Voigt 表示、GPa、压力）
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
 TIMING                      ← 耗时
--------------------------------------------------------------------------------

================================================================================
 END OF UMA CALCULATION
================================================================================
```

---

## 9. 任务类型参考

UMA 模型在不同数据集上训练；每个任务对应特定领域：

| 任务 | 领域 | 体系 | 电荷/自旋 | 应力 | 典型用途 |
|------|------|------|-----------|------|----------|
| `omat` | 无机材料 | 块体晶体 | 可选 | ✓ | 电池材料、固态电解质、氧化物 |
| `omol` | 分子 | 孤立分子 | **必需** | ✗ | 有机化学、药物分子 |
| `oc20` | 催化 (OC20) | 表面 slab | 可选 | ✓ | 多相催化、吸附 |
| `oc25` | 催化 (OC25) | 表面 slab | 可选 | ✓ | 扩展催化基准 |
| `odac` | MOFs | 金属有机框架 | 可选 | ✓ | 气体存储、分离 |
| `omc` | 分子晶体 | 有机晶体 | 可选 | ✓ | 药物、有机电子学 |

---

## 10. 后台任务管理

```bash
# 列出所有任务
uma_calc jobs

# 终止正在运行的任务
uma_calc kill <job_id>

# 清理已完成/失败的任务记录
uma_calc clean
```

任务状态文件存储在 `~/.umakit/jobs/`。

---

## 11. 资源控制

### 11.1 CPU 线程

```bash
export OMP_NUM_THREADS=4
uma_calc sp structure.cif --model uma-s-1.pt
```

### 11.2 GPU 选择

```bash
CUDA_VISIBLE_DEVICES=0 uma_calc sp structure.cif --model uma-s-1.pt --device cuda
```

### 11.3 推理模式

| 模式 | 最适用于 |
|------|----------|
| `default` | 一般用途、SP、OPT |
| `turbo` | MD、大体系、生产环境 |

---

## 12. 故障排除与常见问题

### 12.1 常见错误

#### "No edges found in structure"（未找到边）

**原因：** 模型无法为结构构建邻接图。原子距离太远或 PBC 设置错误。

**解决方案：**
1. 检查输入结构文件
2. 确保原子间距在 ~6 Å 以内
3. 周期性体系用 `omat`，分子用 `omol`

#### CUDA 显存不足

**解决方案：**
1. 切换到 CPU：`--device cpu`
2. 使用较小的模型

#### MD 原子爆炸

**解决方案：**
1. 预弛豫默认启用
2. 先运行几何优化：`uma_calc opt ...` 再 `uma_calc md CONTCAR ...`
3. 降低初始温度

---

## 13. 性能指南

| 体系 | 原子数 | CPU（8 核） | GPU（RTX 3080） |
|------|--------|-------------|-----------------|
| Li₃PS₄（块体） | 28 | 2-3 s | 0.5-1 s |
| Cu slab（3×3×4） | 144 | 15-20 s | 3-5 s |
| MOF-5 | 424 | 60-90 s | 15-20 s |

---

## 14. 使用示例

### 14.1 电池材料能量

```bash
uma_calc sp LLZO.cif --model uma-s-1.pt --task omat --device cuda
```

### 14.2 表面弛豫

```bash
uma_calc opt Pt111_slab.cif \
    --model uma-s-1.pt --task oc20 \
    --fmax 0.02 --max-steps 300 --optimizer FIRE --device cuda
```

### 14.3 NVT 分子动力学

```bash
uma_calc md CONTCAR --model uma-s-1.pt \
    --ensemble NVT --temp 400 --steps 100000 --device cuda
```

### 14.4 批量筛选

```bash
uma_calc batch candidates/ --model uma-s-1.pt --calc-type sp --pattern "*.cif"
```

### 14.5 Python API 吸附能

```python
from umakit.api import calculate_adsorption_energy
result = calculate_adsorption_energy(
    adsorbed_structure="CO_on_Pt.cif",
    gas_structure="CO.xyz",
    surface_structure="Pt_slab.cif",
    model_path="uma-s-1.pt", task="oc20", device="cuda",
)
print(f"吸附能: {result['adsorption_energy']:.4f} eV")
```

---

## 15. 许可证

本项目基于 MIT 许可证开源。

版权所有 (c) Meta Platforms, Inc. and affiliates.
