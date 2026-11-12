# Unarchived — Journal 与交付更新（2026-11-12）

本文记录最新文档交付状态；场景与路线详情见 `Unarchived-WallRoutes-Dusk-Handoff-2026-11-11.md` 顶部的 11/12 灯光及自发光更新。旧交接里“Google Doc 未修改／需用户自己粘贴”及旧曝光截图待拍的说明已经过时。

## 已更新的 journal

[Game Project Brief — Unarchived](https://docs.google.com/document/d/1Utr5ccv5NC9HCm2NgRGDFFgeYQBoBt1qhgIuWpJBIUc/edit?tab=t.qeetsadecfvq)，仅编辑既有 `11/12 — Lighting & Game System` 页签 `t.qeetsadecfvq`，没有新增重复页签。

- 计划稿改为实际完成记录：暖橙黄昏、局部冷光、证物本体自发光、贴墙路线和 Dialogue + Evidence。
- 插入 10 张实际图片：Environment Light Mixer、曝光、Unbound、四组 Before/After、公告自发光、最新 E 交互、此前 END / LEAVE 通关证明。
- 删除四处 After 和游戏系统图片的占位内容。
- 明确区分 11/05 历史图片与 11/11 拍摄的、带课堂参考球的改造前基线；11/12 After 与后者匹配机位、90° FOV 和 2208×1273 原始取景。
- 11/05 页签 body 与编辑前逐项序列化比对一致；其他历史页签没有执行写入。
- 通关图使用 `wallroute/shots/Final_Completion_WallRoutes00000.png` 裁剪，实际可见两条证据、最终选择和 END / LEAVE；不再误用选择前的图片。图注明确其为 11/11 功能验证，不声称在最终材质调整后重跑了全流程。
- 保留下一周天气/VFX 的计划性质，未把已有雾的参数调整写成新天气系统。
- 待人工试玩、旧 HUD 台词、提示朝向、南侧楼梯栏杆，以及 ABC Tier List / Asset Manager 的独立复核仍如实列为未完成。

读回收据：`Saved/JournalUpdate20261112/journal_receipt.json`，10 个 inline image、无图片占位符、历史内容保持。最终正文副本：`Journal_Final_Text.txt`。

## 图像及本地交付

主工作目录：`D:\StartOfTheJourney 5.8\Saved\JournalUpdate20261112`。

桌面交付：`D:\某时之神社的双子猫娘\Unarchived_LightingPass_2026-11-12`。

- `Lighting_Before_After`：重新渲染四张 After，更新四张带日期的左右对比，Before 保留原数据；两边都可见灰球、白球和铬球。
- `Lighting_Setup`：实际 UI 显示 Sun 300、SkyLight 0.9、Manual Exposure −4.25、关闭物理相机曝光和 Unbound；更新参考球图和公告自发光图。旧 ColorGrading 面板已移入归档，避免把旧值当作当前证明。
- `Traversal_Iteration`：更新 After、Before_After，并增加 Photograph 自发光图。其他 11/11 路线细节及落点图保留，报告注明其日期与用途。
- `Game_System`：新增 `Notice_Interaction.png`（11/12 当前版本）；新增 `Completion_Validated_2026-11-11.png`，同时修正旧 `Evidence_Interaction.png` 指向真正的通关截图。旧的选择前图已归档。
- `Implementation_Report.txt` 和 `GoogleDoc_Captions.txt`：更新到最终参数、图像来源、实际验证范围和在线 journal 已更新状态。
- 旧版交付保留在桌面 `Archive_PreviousVersion_20261112`，工程内还有 `Saved/JournalUpdate20261112/Archive/PreviousDelivery` 副本。11/05 原图目录未改。

同步脚本为 `update_delivery.ps1`，文件校验清单为 `delivery_manifest.json`。脚本已经执行，勿把它当成未完成步骤重复运行并覆盖归档。

## 验证与场景状态

- 11/12 新截图使用真实 PIE：正常出生点 → 街道 → Death Notice，脚本控制真实移动，实际 IA_Interact 输入打开对话；无瞬移、飞行。`wallroute/tests/journal_notice_20261112.json` 为 passed，3/3 点；对话可见状态在 `Game_System/Notice_Interaction_State.json`。
- 本次没有重跑完整调查流程。旧完整通关、重复证据防护和五条路线测试沿用前次日志并注明版本；未宣称为人工盲测。
- 标准 Google `files.export` 返回 403，改用已连接 Drive 的流式下载成功导出完整文档 PDF（11 个页签、68 页）。内部检查文件为 `Journal_AllTabs_Final.pdf`。
- 使用 PDF Skill 的只读渲染流程检查第 60–68 页；修正了误继承的标题样式、跨页的对比说明和错误的通关图选择。最终渲染在 `PDF_Final_QA`；图片及图注无裁切或重叠。此 PDF 包含其他历史页签，约 90 MB，仅作为内部核查副本。
- 拍摄时临时移动/显隐的四个 CaptureOnly 参考 Actor 已恢复原位置和可见性，并保存。`capture_restore.json` 与 `final_editor_state.json` 可核对。
- 最终编辑器状态：1899 Actor，367 个 `WR_*`，参考物恢复错误 0，dirty_maps=[]，dirty_content=[]，PIE=false。
- 未修改玩法蓝图、跳跃、交互或路线；没有执行 Diversion 提交、合并或发布。前次 dv agent 启动失败情况仍需未来版本控制操作前另行检查。
