# 基于 3DGS 与 AIGC 的多源资产生成与融合

本仓库对应一个“全链路”3D 视觉作业项目，目标是在同一套工程中完成四条路线：

1. `物体 A`：真实多视角采集 -> `COLMAP` -> `3D Gaussian Splatting`
2. `物体 B`：文本 Prompt -> `threestudio` -> 3D 虚拟资产
3. `物体 C`：单张真实图片 -> 去背景 -> `Zero123 / threestudio`
4. `背景场景`：`Mip-NeRF 360` 场景 -> `3D Gaussian Splatting`

最终再将四类结果统一到 Blender 场景中完成融合渲染，并导出静态图、漫游视频和实验报告。

## 项目亮点

- 同时覆盖真实重建、文本生成、单图生成、场景重建四种 3D 资产来源。
- 在同一工程中统一管理数据准备、训练入口、导出脚本和最终融合流程。
- 提供最终提交所需的：
  - 实验报告源文件
  - 最终场景文件
  - 最终静态图与视频
  - 模型权重清单

## 外部链接

- GitHub Repository：
  `TODO_GITHUB_REPOSITORY_LINK`
- Model Weights：
  `TODO_MODEL_WEIGHTS_LINK`
- Access Code：
  `TODO_ACCESS_CODE_IF_NEEDED`

以上链接需在公开提交前由你本人回填为真实可访问地址。

## 仓库结构

```text
space_intelligent/
├─ configs/
│  └─ pipeline.json
├─ data/
│  ├─ object_a/
│  ├─ object_c/
│  └─ background/
├─ docs/
│  ├─ final_submission_report.md
│  ├─ final_submission_report_strict.tex
│  ├─ final_acceptance_audit.md
│  ├─ submission_hparams_metrics.md
│  ├─ model_weights_manifest.md
│  └─ figures/
├─ outputs/
├─ scripts/
│  ├─ prepare_object_a.py
│  ├─ prepare_object_b.py
│  ├─ prepare_object_c.py
│  ├─ prepare_background.py
│  ├─ remove_background.py
│  ├─ sync_object_a_to_gs_source.py
│  ├─ run_a_quality_resume.ps1
│  ├─ run_b_resume_5000.ps1
│  ├─ run_c_low_resource_resume.ps1
│  ├─ run_c_export_from_600_obj.ps1
│  └─ export_submission_curves.py
├─ workspace/
│  └─ blender_stage/
└─ README.md
```

## 环境配置

### 1. Conda 环境

推荐直接使用根目录的 [environment.yml](file:///D:/space_intelligent/environment.yml)：

```powershell
conda env create -f environment.yml
conda activate space_intelligent_submission
```

如果你已经有项目中的 `nedge` 环境，也可直接复用，只需确保：

- `python`
- `pytorch`
- `lightning`
- `omegaconf`
- `tensorboard`
- `matplotlib`
- `opencv-python`
- `rembg`
- `onnxruntime`
- `trimesh`
- `xatlas`
- `PyMCubes`

等依赖可用。

### 2. 外部仓库

本项目依赖以下外部仓库：

- `gaussian-splatting-win`
- `threestudio`
- `COLMAP`

当前本地配置参考 [pipeline.json](file:///D:/space_intelligent/configs/pipeline.json)：

- `tools.python`
- `tools.ffmpeg`
- `tools.colmap`
- `repos.gaussian_splatting`
- `repos.threestudio`

## 数据准备

### 1. 物体 A

- 原始输入：
  `data/object_a/raw_video/VID_20260617_013308.mp4`
- 抽帧输出：
  `data/object_a/frames/`
- COLMAP 输出：
  `data/object_a/colmap/sparse/0`
- 3DGS 输入目录：
  `data/object_a/gs_source/`

### 2. 物体 B

- 输入方式：
  文本 Prompt
- 当前 Prompt 定义在 [pipeline.json](file:///D:/space_intelligent/configs/pipeline.json#L24-L42) 的 `object_b.prompt`

### 3. 物体 C

- 原始输入：
  `data/object_c/raw_image/IMG_20260617_013342.jpg`
- 前景图：
  `data/object_c/prepared/foreground.png`

### 4. 背景场景

- 数据集来源：
  `Mip-NeRF 360 / garden`
- 当前数据目录：
  `data/background/garden`

## 训练与执行命令

以下命令均可在 PowerShell 中直接复制运行。

### 1. Dry Run

```powershell
conda activate space_intelligent_submission
python scripts/prepare_object_a.py
python scripts/prepare_object_b.py
python scripts/prepare_object_c.py
python scripts/prepare_background.py
```

### 2. 物体 A：真实多视角重建

#### 2.1 准备命令

```powershell
conda activate space_intelligent_submission
python scripts/prepare_object_a.py --execute
python scripts/sync_object_a_to_gs_source.py --execute
```

#### 2.2 质量续训

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_a_quality_resume.ps1
```

### 3. 物体 B：文本到 3D

#### 3.1 准备命令

```powershell
conda activate space_intelligent_submission
python scripts/prepare_object_b.py --execute
```

#### 3.2 续训命令

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_b_resume_5000.ps1
```

### 4. 物体 C：单图到 3D

#### 4.1 去背景

```powershell
conda activate space_intelligent_submission
python scripts/remove_background.py data/object_c/raw_image/IMG_20260617_013342.jpg data/object_c/prepared/foreground.png
```

#### 4.2 准备与恢复

```powershell
conda activate space_intelligent_submission
python scripts/prepare_object_c.py --execute
powershell -ExecutionPolicy Bypass -File scripts/run_c_low_resource_resume.ps1
```

#### 4.3 几何导出

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_c_export_from_600_obj.ps1
```

### 5. 背景场景重建

```powershell
conda activate space_intelligent_submission
python scripts/prepare_background.py --execute
```

### 6. 最终场景融合与视频导出

#### 6.1 启动场景工作区

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_next_stage.ps1
```

#### 6.2 导出提交用曲线

```powershell
conda activate space_intelligent_submission
python scripts/export_submission_curves.py
```

#### 6.3 最终 Blender 结果

最终场景与视频构建脚本位于：

- [build_final_submission_scene.py](file:///D:/space_intelligent/workspace/blender_stage/build_final_submission_scene.py)
- [render_submission_preview.py](file:///D:/space_intelligent/workspace/blender_stage/render_submission_preview.py)

## 测试与结果检查

### 1. 场景结果

- 最终 `.blend`：
  [scene_submission_final.blend](file:///D:/space_intelligent/workspace/blender_stage/scene_submission_final.blend)
- 最终静态图：
  [scene_submission_final.png](file:///D:/space_intelligent/workspace/blender_stage/scene_submission_final.png)
- 最终视频：
  [scene_submission_final_preview.mp4](file:///D:/space_intelligent/workspace/blender_stage/scene_submission_final_preview.mp4)

### 2. 报告与核对表

- 最终详细报告：
  [final_submission_report.md](file:///D:/space_intelligent/docs/final_submission_report.md)
- 严格提交版 LaTeX 报告源：
  `docs/final_submission_report_strict.tex`
- 合格性核对表：
  [final_acceptance_audit.md](file:///D:/space_intelligent/docs/final_acceptance_audit.md)
- 超参数与指标表：
  `docs/submission_hparams_metrics.md`
- 权重清单：
  `docs/model_weights_manifest.md`

## 重要说明

- A 和背景的原始结果属于 3DGS / 点云表达，不适合直接作为 Blender 最终渲染输入。
- 因此最终融合阶段采用了“保留原始结果 + 派生 Blender 友好表达”的工程路线。
- C 当前最终导出是 geometry OBJ，最终显示依赖 Blender 材质补充。
- 当前仓库已经补齐本地提交材料，但以下两项仍需你本人在最终提交前完成：
  - 回填 Public GitHub 仓库链接
  - 回填云端模型权重分享链接和提取码

## 引用

如用于课程作业提交，建议同时附上：

- 最终 PDF 报告
- 最终视频
- 最终 Blender 场景
- 模型权重下载链接
