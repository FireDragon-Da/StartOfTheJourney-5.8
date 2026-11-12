# Unarchived：灯光与环境跳跃改造交接（冻结）

> **已过时**：最新状态见 [Unarchived-WallRoutes-Dusk-Handoff-2026-11-11.md](Unarchived-WallRoutes-Dusk-Handoff-2026-11-11.md)（2026-11-11 23:00）。本文保留作历史记录。

冻结时间：2026-11-11 21:05 EST（UTC−05:00）。任务资料目录沿用 20261112 命名。

## 交接结论与用户要求

用户已要求“先冻结现有进度，然后写个交接文档后面继续开工”。本轮已停止场景改造，仅检查保存状态、复制冻结快照和编写本文。后续接手应先阅读本文及原始任务，再等待/遵循用户的继续开工指令。

**当前平台方案未被用户接受，不能标为完成。** 用户指出平台必须紧贴墙壁、融入建筑，可以重新设置跳跃距离。此前沿原有悬空路线添加木板、立柱、斜撑的处理没有满足要求；测试可跳通不能证明外观合格。贴墙重新排布与新的跳跃调参尚未实施。

冻结时只读检查：主关卡 `/Game/Inarchived/Maps/Lvl_TownBlock.Lvl_TownBlock`，1695 个 Actor，`dirty_maps=[]`、`dirty_content=[]`。当前保存资源无未保存项。PIE 已停止。冻结后未再修改 UE 场景。

## 项目、版本控制与快照

- 项目根目录：`D:\StartOfTheJourney 5.8`，使用 Diversion（`dv`），不是 Git 工作流。
- 最近成功记录的分支：`codex/dialogue-pacing-2026-11-05`；云端提交标识 `dv.commit.15`。任务开始前已有约 65 个变更路径，不能全部归为本次修改。
- 本次没有执行提交、合并或发布。冻结时重试 `dv status`，CLI 报 agent 启动超时，未能重新确认最新状态。上次状态见 `Saved\LightingPass20261112\diversion_before_wall_rework.txt`。下次先恢复/检查 `dv status`、`dv diff`，不要擅自提交全部改动。
- **冻结快照**：`Saved\LightingPass20261112\Freeze_20261111_210547\`。包含当前地图、角色蓝图、新窗户材质、两份配置、`.dvignore`、冻结/灯光/墙面采样 JSON，以及原始需求 `Original_Request.txt`。`manifest.json` 记录 9 个资源/状态文件的大小和 SHA256。
- **任务前备份**：`Saved\LightingPass20261112\Backup_20261111_195319\`。与冻结快照用途不同：前者用于查原貌，后者保存当前中间态。不要整目录覆盖恢复；先比对具体资源，避免覆盖用户已有工作。
- 原始附件：`C:\Users\honor\.codex\attachments\086d6438-62ca-480c-974c-c9ed31a34725\已粘贴的文本.txt`，已复制到冻结快照以便持续查阅。

快照是磁盘副本，并非 Diversion 提交；`Saved` 通常被忽略，需保留本机资料目录。

## 当前已保存的实际修改

### 主地图与平台（未验收）

文件：`Content\Inarchived\Maps\Lvl_TownBlock.umap`。

- Photograph 路线 `TRV_Float_NWRoof_01..11` 换为木质检修平台，**保留旧路线的原 XY 绕行**。前 10 块约 210×210×28 cm，末块约 240×185×28 cm；末块石质。增加约 110 个 `LP_Photo_*` 构件（饰边、板缝、托梁、立柱、脚座、斜撑和墙拉结）及街面小棚。这是被用户否定的方案，不应继续扩展或据此宣称建筑融合完成。
- Radio 只处理了末块 `TRV_Float_AlleyFront_09` 的木质表面、阳台支架、檐棚/支柱。其余多组紫色悬空平台还在。
- 原平台组：NWRoof 11、AlleyFront 9、Alley 10、SouthRoofs 12、EastLookout 7，共 49 个落脚平台，另有 3 个 LowWalls。最新逐 Actor 位置、缩放、材质见 `freeze_state.json`；原始全场景见 `initial_state.json`。
- 隐藏了旧的青色 Notice 边框和部分路线/标题引导（`Guide_NoticeFrame*`、`Guide_StreetSign`、Photo/Radio 标题与 Route），没有删除证据。原 Notice 引导灯强度设为 0。实际 E 交互保留。
- Photograph、Radio 的 PromptText 实例字号从 110 改为 22，尚需最终运行时复查。

### 灯光与材质

- Sun：Movable，强度 7.5，俯仰 −14、偏航 165，暖色；SkyLight：Movable，强度 0.7，偏冷，实时捕获。
- 现有 43 个街灯 BP 点光组件：强度 24、半径 540、暖色；仅选定两盏 LinkN 灯开阴影。
- 新增具有可见灯壳/镜片及安装构件的实用灯：Notice 18 cd（半径 520）、Photo 24 cd（680）、Radio 12 cd（460）。Photo/Radio 高处没有直接墙面支撑，后加灯杆/檐部安装结构；这不等于平台已贴墙。
- `WarmGrade`：Unbound、优先级 10，手动曝光，关闭物理相机曝光，Bias +0.3；曝光曲线清空，局部曝光恢复中性；色温 6500，饱和度 0.97，对比度 1.035，轻微暖高光/冷阴影，Bloom 0.15、Vignette 0.12、MotionBlur 0；GI/Reflection 设 Lumen。
- 本地 GameUserSettings 的 GI/Reflection 质量由 0 调至 2。运行时读回 Lumen 漫反射/反射开启，DynamicGI/ReflectionMethod 均为 1，距离场开启。不要只看项目设置就假定运行时生效。
- 新资源：`Content\Inarchived\Town\Materials\MI_Window_LightingPass_20261112.uasset`，继承原 `M_TownWindow`，调整 BaseColor/EmissiveColor，仅用于房屋网格实例的窗户材质槽，未改父材质。
- 三个验证球复用 `/Game/Inarchived/Maps/11_5/` 的 `M_grey`、`M_white`、`M_chrome`，放在 `LightingPass/Validation` 文件夹，标签 CaptureOnly。拍摄脚本会移动/显隐球，后续使用前先读脚本，不要误把测试物摆放当最终环境设计。
- 精确参数见 `final_lighting_state.json`；原灯光状态见 `lighting_before.json`，最初场景/曝光状态见 `initial_state.json`、`details.json`。

### 蓝图及辅助文件

- `Content\ThirdPerson\Blueprints\BP_ThirdPersonCharacter.uasset`：ResolveFinished 中节点 `F3A9B8E3` 的 A 字符串默认值，将字面 `\\n` 修为真正换行加 `+ `，解决 Journal 连写。已编译，0 error / 0 warning，保存；**修复后尚未重新运行验证**。
- 跳跃参数保持原样：JumpZVelocity 500、AirControl 0.35、MaxWalkSpeed 600、GravityScale 1；胶囊半径 35、半高 90、MaxStepHeight 45。用户允许重新调跳跃，但本次尚未调。
- `.dvignore` 增加 `Tools/ziggymar-unreal-mcp/mcp-server/dist/`。Bridge 安装依赖并生成 dist；TypeScript 编译成功，后置 parity 检查因上游假定的插件目录与实际 `Plugins/UnrealMCPBridge` 不同而失败，未修改校验源码。实际连接握手通过。

## 已做测试及其边界

测试使用真实 PIE Pawn 的 `add_movement_input`、`jump` 和视角旋转，通过 Slate tick 自动控制；**无瞬移、飞行或直接写速度**。这是自动操纵的路线测试，不是完整人工游玩，也不能证明自然找路、镜头舒适度或平台外观合格。

| 检查 | 记录及结果 |
| --- | --- |
| 出生点至 Photograph | `photo_ground_to_rooftop_final.json`，18 个点通过，约 30.93 秒（不含阅读/探索） |
| 街面至 Radio | `radio_natural_route.json`，16 个点通过，约 28.5 秒 |
| 自然下楼/返回 | `photo_return_to_notice.json`、`radio_to_questioner.json` 通过 |
| Photograph | 实际 E 阅读、选择 B，证据数变 1；重复完成仍 1，bLastAdded=False |
| Death Notice | 同一最终测试运行中完成，bReadDeathNotice=True |
| Radio | 实际阅读三页并选 A，证据数变 2；重复完成仍 2，bLastAdded=False |
| 最终 NPC | 实际 E 打开 `DT_GuyEnding`，三页后选 Leave，显示 END / LEAVE，bPrototypeComplete=True |

各交互状态文件：`photo_registered_state.json`、`photo_duplicate_state.json`、`notice_complete_state.json`、`radio_registered_state.json`、`radio_duplicate_state.json`、`questioner_open_state.json`、`final_completion_state.json`。

这些成功记录对应旧路线方案；后续贴墙改造必须重新测试。最终字号缩小、无碰撞的灯安装细节和 Journal 换行修复之后，还未做完整 smoke test。`photo_ground_to_rooftop_v2..v5.json` 保留失败调试记录，不能作为当前成功证明。失败曾涉及墙拉结/托梁顶头；恢复原 XY 后才得到最终成功记录。

## 视觉资料、文档与未交付项

所有过程资料位于 `Saved\LightingPass20261112\`。

- `01_Spawn_Before.json.png` 至 `04_Radio_Before.json.png` 是本次修改前真实拍摄；同名 `_After.json.png` 是当前中间态。另有 `Traversal_Before.json.png` / `Traversal_After.json.png`。After 展示的是**冻结且未验收的方案**。
- 小写 `traversal_before.json.png` 是早期错误朝向的天空图，不要使用。相机数据在 `camera_*.json`；相机脚本 `camera.py`。
- `Environment_Lights.json.png` 是真实 Environment Light Mixer 界面；PostProcess 设置截图尚未完成。
- `Evidence_Interaction00000.png`、`Photograph_Recorded00000.png`、`Final_Completion00000.png` 使用 Shot showui，含实际 HUD。`Evidence_Interaction.png` 使用 HighResShot，不含 UI，不能当交互证明。
- 实际桌面目录：`D:\某时之神社的双子猫娘\Unarchived_LightingPass_2026-11-12`。目前仅 `Original_Journal_Before` 放入了 11/05 的四张历史截图；其他交付子目录尚未整理完成。没有正式 Implementation Report。
- 原 Google Doc：[Game Project Brief — Unarchived](https://docs.google.com/document/d/1Utr5ccv5NC9HCm2NgRGDFFgeYQBoBt1qhgIuWpJBIUc)。**尚未写入任何在线修改**。保留原 11/05 页签及图片。后续只更新既有 11/12 — Lighting & Game System 页签 `t.qeetsadecfvq`；11/05 页签为 `t.gm5kmu6u3ji2`。
- 尚缺：被接受的贴墙平台方案、完整人工自然游玩、最终改动回归、PP 界面证据、最终对比排版/报告、桌面交付整理、Google Doc 11/12 页更新及导出视觉检查。不能把原任务整体写成完成。

## 继续开工时的优先事项

1. 先查看冻结地图与用户否定意见，读取项目 `AGENTS.md`、UE MCP 技能、原始任务全文；检查 Diversion 和实时编辑器状态。不要自动恢复旧备份或运行历史改造脚本。
2. 以建筑自身的墙体、窗、檐口、阳台/检修走道关系重新设计贴墙路线。用户要求覆盖悬空平台问题，不限于 Photograph；可先把一条重点路线做出可信效果，再推广到其他组。单纯重新染色、给原悬空路径补长杆/斜撑没有满足要求。
3. 用户已允许重新设置跳跃距离。根据建筑尺度同时决定落脚点、横向间距和高度差，再验证胶囊净空、顶头、墙角、相邻屋顶和碰撞。不要受原 JumpZ=500 或原 XY 约束。
4. 改造前区分旧 `TRV_*`、本次被否定的 `LP_Photo_*` 附加物与原始建筑/证据；备份后再逐项处理。保留证据、交互与剧情，不要粗暴删除全图前缀对象。
5. 新路线和照明完成后，重新从地面真实移动测试、交互、重复收集与最终 NPC；再做人工找路/镜头/美术检查与固定相机对比。最后更新报告、原 Google Doc 和桌面资料。

贴墙改造前只做过只读探测，保存于 `wall_rework_before.json`。例如 Photo 建筑南墙在不同高度采样约 Y=2416–2421，雨棚突出约 Y=2368；Radio 南墙约 Y=2818–2827，雨棚约 Y=2767。**这些仅是个别射线采样，不是可套用到整面墙/屋顶的平面**；需对每个落脚点重新测墙、屋檐与头部净空。本次没有应用新的贴墙坐标或证据位置。

## MCP 恢复入口与操作注意

当前会话没有原生 UE 工具条目，已验证以下三个服务；下次先检查可用性，不要重复启动编辑器或盲目重装。

| 服务 | 入口 |
| --- | --- |
| official | `http://127.0.0.1:8000/mcp`；`list_toolsets`、`describe_toolset`、`call_tool` |
| unreal-mcpython | `D:/sotj-mcpython/.venv/Scripts/python.exe -m unreal_mcp.main`，编辑器端 TCP 12029 |
| unreal-bridge | `D:/node.exe D:/StartOfTheJourney 5.8/Tools/ziggymar-unreal-mcp/mcp-server/dist/index.js`；PROFILE=search、MODE=standard，编辑器端 TCP 8765 |

辅助客户端：`Saved\LightingPass20261112\mcp.mjs`。例如从项目根目录执行只读脚本：

```powershell
& D:/node.exe Saved/LightingPass20261112/mcp.mjs python exec 'D:/StartOfTheJourney 5.8/Saved/LightingPass20261112/freeze_readonly.py'
```

上例会重新生成诊断 JSON，适合恢复检查，不应覆盖冻结快照。沙箱环境可能需要为本机回环连接使用现有工具授权机制。UE 操作必须串行。不要为连接问题再次启动第二个 UnrealEditor；之前误启动的重复进程已清理，原编辑器保留。

- **不要盲跑** `implement.py`、`restore_route_spacing.py` 或其他历史实现脚本：它们可能恢复被否定的路线、覆盖后续曝光/灯具修正。
- Python 输出尽量只打印一次 JSON；引擎 warning 会干扰客户端解析。先检查脚本的写入范围。
- Rotator 必须显式关键字 `pitch=...`、`yaw=...`、`roll=...`；位置参数在此版本导致过相机错误。Viewport 操作先取 active viewport config key。
- `line_trace_single` 返回 HitResult 或 None；不要假定 bool 元组。优先 `TraceTypeQuery.ECC_VISIBILITY`，旧枚举会发 warning。
- 分离 PIE 窗口时，Bridge 的 viewport screenshot 可能拍到编辑器而非游戏。交互证据用真实游戏窗口或 `Shot showui`；HighResShot 不含 UMG。

本交接只记录现状和后续入口，不构成平台方案验收或最终任务交付。

---

## 续作记录（2026-11-11 22:45 EST）：贴墙路线已实施，待用户验收

以上为冻结时的原文，保留不改。本节记录续作后的实际状态。工作目录 `Saved\LightingPass20261112\wallroute\`，续作前备份 `Saved\LightingPass20261112\Backup_20261111_211800_PreWallRoutes\`（地图、角色 BP、全量 Actor 清单）。

- **悬空平台已全部移除**：五组 `TRV_Float_*`（49 块 + 3 面 LowWall + 5 个 Root），以及被否定的 109 个 `LP_Photo_*` / `LP_Radio_*` 脚手架件。删除前已确认无 BP、关卡或配置引用。原有绿色楼梯/走廊网络（约 1200 个 `TRV_*`）未动。
- **新路线**：367 个 `WR_<Route>_*`，位于 `Traversal/WallRoutes/<Route>`，标签 `WallRoute`。每件逐件追踪墙面并嵌入 2 cm。可踩顶面为 BlockAll，托架、装饰为 NoCollision。数据定义在 `wallroute/routes.py`，生成脚本 `build_wall_routes.py` 按路线幂等重建；离线校验 `validate.py` 检查净空和跳跃弧线。
  - Photograph：NWBlock_01 东立面 → 东北角木平台 → 北立面 → 屋顶露台 → 屋檐 belvedere（照片未移动）。
  - Radio：AlleyE 巷侧墙 → 屋顶 → 屋檐木阳台（收音机未移动）。
  - Carbon：AlleyW 巷侧墙 → 屋顶 → 巷侧石阳台（未移动）。
  - Stopped Watch：SS_03/SS_05 夹缝两墙交替 → 女儿墙下检修走道；记录 Z 由 1522 改为 1452。
  - Worn Key：NEBlockW_01 走廊花箱 → 遮雨棚 → 东立面平台 → 东檐下瞭望阳台；记录由 (3000,270,1157) 移至 (3490,1430,1007)。另补上了东走廊外栏的缺口。
- **跳跃**：JumpZVelocity 500→600，AirControl 0.35→0.45，运行时读回一致。全图无顶部在 128–190 cm 之间的围墙或栏杆，未打开新的越界通道。
- **灯具**：Photo/Radio 灯头分别抬到 1565/1515，避免挡头；灯壳、镜片改为 NoCollision；裸灯杆换成女儿墙上的灯柱。强度、半径、颜色未改。PPV、Sun、SkyLight、Lumen 未改。
- **黄昏微调（22:55，按用户要求“更偏向黄昏一点”）**：
  - Sun：俯仰 −14°→−8°，强度 7.5→6.5，颜色 (255,231,203)→(255,205,155)。
  - SkyLight：0.7→0.62，颜色 (218,224,255)。
  - PPV：Bias +0.3→+0.45，WhiteTemp 6500→6100，高光增益 (1.05,0.99,0.92)，阴影增益 (0.96,0.99,1.04)。
  - 原值见 `wallroute\dusk_before.json`，地图备份在 `PreDusk\`。桌面上的 After、对比图和参考球截图已按新灯光重拍；PPV 截图仍是调整前拍的（显示 0.3）。
- **测试**（真实输入，无瞬移；选项为真实鼠标点击）：五条路线均从出生点走通。同一会话完成 Notice → Photograph（B，重复仍 1）→ 原路下楼 → Radio（A，重复仍 2）→ 原路下梯 → The Guy（Leave，`bPrototypeComplete=True`）。三个可选记录的 E 交互均正常；Journal 换行和 PromptText 22 在运行时已确认。记录见 `wallroute\tests\`。
- **交付**：桌面 `D:\某时之神社的双子猫娘\Unarchived_LightingPass_2026-11-12\` 已整理完成，含 4 组同机位 Before/After 与并排图（After 用 HighResShot 2208x1273 渲染，与 Before 取景一致）、PPV 截图 4 张、参考球、路线图、游戏系统截图、`Implementation_Report.txt`、`GoogleDoc_Captions.txt`。Google Doc 未编辑。
- **仍待处理**：
  1. HUD 文案仍写“above the floating routes”（`BP_ThirdPersonCharacter` > RefreshJournal 最后一个 SetText(JournalGoal)，节点 701AECA9），The Guy 台词仍写“Follow the floating routes…”（`BP_TownQuestioner` > Talk）。MCP 无法写入 FText 字面量，需在编辑器中手改。
  2. Photograph/Radio 的世界提示文字从阳台一侧看是镜像的。
  3. 南走廊栏杆横跨 Stair_02 入口（原有问题）。
  4. 未做盲测或人工美术验收；Diversion 未提交。
