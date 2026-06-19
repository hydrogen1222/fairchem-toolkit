from __future__ import annotations

import os
import time

from ase.io import read
from fairchem.core import FAIRChemCalculator

print("1. 正在读取晶体结构...")
# 读取你放在同一个文件夹下的 cif 文件
atoms = read("Li6PS5Cl.cif")
print(f"结构读取成功！该体系共有 {len(atoms)} 个原子。")


print("2. 正在加载 UMA 模型 (使用 CPU，这可能会稍微花一点时间)...")
# 这里需要将 "uma_pretrained.pt" 替换为你实际下载的 UMA 模型权重文件的名字/路径
# cpu=True 强制模型在你的笔记本 CPU 上运行
checkpoint_path = "uma-s-1.pt" if os.path.exists("uma-s-1.pt") else "uma_pretrained.pt"
calc = FAIRChemCalculator.from_model_checkpoint(
    checkpoint_path,
    task_name="omat",
    device="cpu",
)
atoms.calc = calc

print("3. 开始计算体系能量和受力...")
start_time = time.time()

# 这一步是核心：让模型进行推理
energy = atoms.get_potential_energy()
forces = atoms.get_forces()

end_time = time.time()

print("================ 计算完成 ================")
print(f"耗时: {end_time - start_time:.2f} 秒")
print(f"体系总能量: {energy:.4f} eV")
print(f"第一个原子的受力: {forces[0]} eV/A")
