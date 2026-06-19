# UMAKit Refactor Design

Date: 2026-06-19

## Problem Summary

`uma/umakit/` 是一个基于 FAIRChem UMA 模型的 VASP 风格计算器，提供 CLI 和 TUI 两种交互模式。当前代码存在以下问题：

1. **5 个文件模块头部格式错误** — `from __future__` 位置不对，版权块误用 docstring
2. **TUI CSS 语法错误** — `font-size: 90%` 不是 Textual 合法属性
3. **CLI/TUI/API 三条执行路径各自重复实现** — 同样的结构读取、模型加载、Runner 创建逻辑写了三遍
4. **TUI 用 threading 配合 asyncio 框架** — 无法真正取消任务，架构脆弱
5. **`BatchRunner` 的 `parallel` 参数是死代码** — 只串行循环
6. **无后台任务管理** — 长计算离开终端就断
7. **进度信息混乱** — 只有文本日志，无结构化进度事件

## Design

### 1. Execution Engine Layer

新增 `uma/umakit/engine.py`，提供 `CalculationEngine`，作为 CLI/TUI/API 三条路径的**唯一执行入口**。

```python
@dataclass
class ResourceSettings:
    torch_num_threads: int | None = None
    activation_checkpointing: bool = True

@dataclass
class EngineConfig:
    calc_type: Literal["sp", "opt", "md", "batch"]
    model_path: Path
    task: str
    device: str
    inference_mode: str
    output_dir: Path
    job_name: str | None
    options: dict      # 差异化参数: {"fmax": 0.05, "cell_opt": True, ...}
    resource: ResourceSettings = field(default_factory=ResourceSettings)
    detach: bool = False

class CalculationEngine:
    @classmethod
    def from_config(cls, config: EngineConfig) -> CalculationEngine: ...

    def run(self, atoms: Atoms, progress_callback=None) -> dict: ...
    async def run_async(self, atoms: Atoms) -> AsyncIterator[ProgressEvent]: ...
    def run_batch(self, files: list[Path]) -> BatchSummary: ...
```

三条路径各退化为薄适配层：

- **CLI**: `argparse` → `EngineConfig` → `engine.run()`
- **TUI**: 表单 widget → `EngineConfig` → `engine.run_async()` → 实时刷新 UI
- **API**: 函数参数 → `EngineConfig` → `engine.run()`

底层模块（`BaseRunner` 子类、`UMACalculator`、Writer 类、`IncarConfig`）**不动**。

### 2. Progress Protocol

新增 `uma/umakit/protocols.py`，定义轻量进度事件，不改 Runner 核心逻辑。

```python
@dataclass
class ProgressEvent:
    phase: str              # "loading_model" | "running" | "writing_output" | "done"
    message: str            # 人可读
    step: int | None        # 当前步（opt/MD 有值，SP 为 None）
    total_steps: int | None # 总步数（opt=MAX_STEPS, MD=steps, batch=file_count, SP=None）
    extra: dict | None      # {"energy": -123.4, "fmax": 0.03, "temperature": 300.0, ...}
```

各计算类型显示策略：

| 类型 | step/total_steps | 进度指示方式 |
|------|-------------------|-------------|
| SP | None / None | indeterminate spinner |
| OPT | 当前步 / MAX_STEPS | 步数计数，可能提前收敛 |
| MD | 当前步 / steps | 确定性进度条 |
| BATCH | 当前文件 / 总文件数 | 确定性进度条 |

TUI 中：`ProgressBar` 支持 indeterminate 模式，SP 计算时不会造假进度。

### 3. TUI 修复

#### 3.1 asyncio worker 替代 threading

```python
class RunScreen(Screen):
    _task: asyncio.Task | None = None

    async def on_mount(self) -> None:
        self._task = asyncio.create_task(self._run_calculation())

    async def _run_calculation(self) -> None:
        engine = CalculationEngine.from_config(...)
        async for event in engine.run_async(atoms):
            self._update_progress(event)
            self._log(event.message)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-btn":
            self._task.cancel()   # 真正取消
```

Engine 端用 `run_in_executor` 把同步 Runner 调度到线程池，通过 `asyncio.Queue` 桥接进度事件回主线程。

#### 3.2 CSS 修复

- 删除 `font-size: 90%`
- `#main-container` 的 `width: 80` → `width: 100%`
- 所有容器用 `1fr` / `100%` 自适应终端缩放

#### 3.3 路径输入人性化

- 实时校验 + 状态显示（已有基础，增强提示）
- 路径用 `pathlib.Path`，天然跨平台
- 提示文案说明相对路径用法（Windows 用 `\`，Linux/Mac 用 `/`）

### 4. Job Management

计算任务以**独立子进程**运行。TUI/CLI 是任务控制器，不是执行器。

#### 4.1 任务状态文件

位置：`~/.umakit/jobs/`

```
~/.umakit/jobs/
├── 2026-06-19_14-30-15_Li3PS4_sp.json
└── logs/
    └── 2026-06-19_14-30-15_Li3PS4_sp.log
```

```json
{
    "job_id": "2026-06-19_14-30-15_Li3PS4_sp",
    "status": "running",
    "calc_type": "sp",
    "structure": "D:/data/Li3PS4.cif",
    "formula": "Li3PS4",
    "natoms": 28,
    "pid": 12345,
    "device": "cuda",
    "started_at": "2026-06-19T14:30:15",
    "finished_at": null,
    "log_file": "~/.umakit/jobs/logs/2026-06-19_14-30-15_Li3PS4_sp.log",
    "progress": {"phase": "running", "message": "Calculating..."},
    "results": null,
    "error": null
}
```

#### 4.2 操作接口

| 操作 | CLI | TUI |
|------|-----|-----|
| 提交并等待 | `uma_calc sp ...` | Run 按钮 |
| 提交到后台 | `uma_calc sp ... --detach` | Run + "Background" 复选框 |
| 列出任务 | `uma_calc jobs` | Jobs 屏幕 |
| 查看进度 | `uma_calc attach <id>` | Jobs 屏幕 → 点击任务 → 实时日志 |
| 终止任务 | `uma_calc kill <id>` | Jobs 屏幕 → Cancel 按钮 |
| 清理已完成 | `uma_calc clean` | Jobs 屏幕 → Clean 按钮 |

#### 4.3 跨平台进程管理

```python
def kill_job(pid: int) -> None:
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/PID", str(pid), "/F"])
    else:
        os.kill(pid, signal.SIGTERM)
```

### 5. Resource Control

通过 `InferenceSettings` 暴露 fairchem 的资源控制参数：

- `torch_num_threads` — 控制 CPU 线程数
- `activation_checkpointing` — 降低 GPU 显存占用

GPU 设备选择：通过 `CUDA_VISIBLE_DEVICES` 环境变量（PyTorch 标准机制）。

## File Manifest

### 新增文件
- `uma/umakit/engine.py` — CalculationEngine
- `uma/umakit/protocols.py` — ProgressEvent dataclass
- `uma/umakit/jobs.py` — JobManager 任务管理

### 修改文件
- `uma/umakit/runners/md.py` — 修复头部 + 添加 progress callback
- `uma/umakit/runners/optimization.py` — 添加 progress callback
- `uma/umakit/runners/singlepoint.py` — 添加 progress callback
- `uma/umakit/runners/batch.py` — 实现真并行 + progress callback
- `uma/umakit/runners/base.py` — BaseRunner 加 progress_callback 参数
- `uma/umakit/tui/app.py` — 修复头部 + 注册 Jobs 屏幕
- `uma/umakit/tui/main_screen.py` — 添加 Jobs 入口
- `uma/umakit/tui/config_screen.py` — 修复 CSS + 增强路径提示 + detach 选项
- `uma/umakit/tui/run_screen.py` — 修复头部 + asyncio worker 重写
- `uma/umakit/api.py` — 修复头部 + 改用 Engine
- `uma/umakit/logger.py` — 修复头部
- `uma/umakit/cli.py` — 简化 handler + 新增 jobs/kill/clean 子命令
- `uma/umakit/calculator.py` — 支持 ResourceSettings 参数
- `uma/umakit/__init__.py` — 延迟导入

### 删除文件
- `uma/uma_calc.py` — 功能合并到 `cli.py`

## Clarifications

### Batch 并行策略
`BatchRunner` 的 "真并行" 使用 `concurrent.futures.ThreadPoolExecutor`（不是 `multiprocessing`）。每个 worker 线程独立加载模型并运行计算。线程数可配置，默认 `min(4, os.cpu_count())`。注意：GPU 模式下多线程共享同一 GPU 可能导致显存竞争，因此 GPU 时默认 `max_workers=1`，用户可覆盖。

### EngineConfig.options 校验
`CalculationEngine.__init__` 中根据 `calc_type` 校验 `options` 的必需/可选键：
- SP: 无必需键
- OPT: 可选 `fmax`, `max_steps`, `optimizer`, `cell_opt`, `fix_symmetry`
- MD: 可选 `ensemble`, `temperature`, `timestep`, `steps`, `friction`, `save_interval`, `pre_relax`, `pre_relax_steps`, `pre_relax_fmax`
- BATCH: 可选 `pattern`, `sub_calc_type`

未知键会 warn 但不会报错（向前兼容）。

### ResourceSettings 与 inference_mode 的优先级
`ResourceSettings` 中的字段如果显式设置（非 None/默认值），覆盖 `inference_mode` 的预置值。如果未显式设置，则 inference_mode 的预置优先。即：**显式设置 > inference_mode 预设 > 全局默认**。

### TUI Jobs 屏幕布局
Jobs 屏幕用 `DataTable` widget 显示任务列表，列：ID、Status（带颜色标记）、Type、Formula、Progress。按 Enter 进入 `JobDetailScreen`（`Log` widget 实时 tail 日志文件）。刷新：每 2 秒自动重新读取 `~/.umakit/jobs/*.json`。Cancel 按钮调用 `kill_job()`。

### 新增测试（冒烟测试，至少 5 个）
- `tests/core/umakit/test_engine.py` — Engine 构造和配置
- `tests/core/umakit/test_config.py` — IncarConfig 解析
- `tests/core/umakit/test_protocols.py` — ProgressEvent
- `tests/core/umakit/test_jobs.py` — JobManager 状态读写
- `tests/core/umakit/test_calculator.py` — UMACalculator 参数验证

## Non-Goals

- 不重构 BaseRunner 子类的核心计算逻辑
- 不修改 Writer 类
- 不引入新的第三方依赖
- 不修改 fairchem-core 的任何代码
