# Unarchived：贴墙路线 + 黄昏灯光 交接（2026-11-11 23:00 EST）

> **2026-11-12 Journal／After 图片交付已更新**：请先读 `Docs/Unarchived-Journal-Delivery-Update-2026-11-12.md`。原 Google Doc 的 11/12 页签已经写入 10 张实际图片与完成说明，11/05 历史内容保持；桌面 After、对比图、实际设置截图与报告已同步。下文“需用户自行粘贴”和旧版截图待更新事项属于历史状态，已由该更新记录取代。

> **2026-11-12 证物本体自发光补充**：11 个 `BP_TownRecord` 实例的可见 `SignBoard` 材质槽 0 已统一设为 `/Game/Inarchived/Town/Materials/MI_EvidenceSelfGlow`。其独立父材质 `M_EvidenceSelfGlow` 复制自项目内 M_SimpleGlow，仅保留 Color → Emissive 的直接输出，使用 Opaque / Unlit，关闭 Color 的 Custom Primitive Data；HDR Color 为线性 (6,42,70,1)。原父材质和原材质实例未改。不能直接复用原粒子材质：其透明/粒子数据路径会令静态模型不发光。现为模型本体发冷光，沿用原位置、网格、碰撞、文字与交互。模型当前仍是原有方块/牌板，此次仅改材质。地图和两个新材质已保存；本轮前地图、原槽位及验证资料在 `Saved/LightingRefine20261112/EvidenceSelfGlow/`，有效最终预览为 `Photo_Opaque.png`，之前的 SelfGlow/Final 截图为调试失败中间态，勿用作交付。
>
> DeathNotice 自身的 SignBoard 原本隐藏，可见公告面实际为 `NewsStand.Poster`，因此该 Poster 也应用同一自发光实例，未改变隐藏状态。其原材质记录于 `poster_before.json`；最终公告预览为 `Notice_SelfGlow_Final.png`。已在 PIE 逐项核对 11 个记录材质、Opaque 模式及禁用 Custom Primitive Data，记录在 `final_pie_verified.json`；未改动/重测剧情流程。调试期间的 `Game_Final00000.png` 尚未包含独立 Poster 的补充，不是最终公告证明。

> **2026-11-12 灯光更新**：用户要求“证物部分发冷光，整体明亮暖色，城镇呈暖橙色黄昏”。本次仅调整主地图灯光和本机画质，以下新增记录取代旧灯光数值；路线、证据位置、跳跃与交互没有更改。
>
> - Sun：300 lux，Pitch −10° / Yaw 165°，sRGB (255,205,155)，保持温度开关关闭。提高到黄昏照度后，Manual Exposure Bias 配套改为 −4.25，不能只恢复其中一个参数。WhiteTemp 回到 6500；高光 Gain (1.025,1,0.965,1)、阴影 Gain (1.01,1,0.985,1)。
> - SkyLight：0.9，sRGB (255,239,219)。Fog 密度 0.00002、StartDistance 2000、线性散射色 (0.30,0.22,0.15)，去掉原有粉紫雾影响。云材质只读检查：Coverage −0.2、Density 0.008，未改引擎资产。
> - Notice / Photo / Radio 的原灯改为冰蓝 sRGB (125,200,255)，分别 1000 / 1440 / 1120 cd；现有灯位、照射方向和范围保留。WornKey、StoppedWatch、CarbonRegister 各加一盏局部冰蓝点光 `LR_Cool_Record_*`，240 cd、半径 200、无阴影、Movable，位于记录上方 65 cm。
> - 为配合新的照度/曝光，43 盏街灯、3 个 Signpost、FinalGate 的原有局部灯强度统一乘 40。**此项已经应用，切勿再次乘 40。** 街灯现在为 960。旧 `dusk_apply.py` 参数会破坏这次照度/曝光配套，不要直接重跑。
> - 当前运行发现 GI/Reflection 质量实际为 0，已通过 GameUserSettings 调为 2 并保存；PIE 读回 Lumen DiffuseIndirect/Reflections 均为 1。该质量设置是本机 Saved 配置，其他机器仍需检查实际画质。
> - 保存后 1899 Actor（新增 3 灯），`WR_*` 仍为 367；11 个记录 Actor 位置逐项比对未变。JumpZ=600、AirControl=0.45 保持；地图保存成功、dirty_maps=[]。
> - 已查看广场、Photo、Notice、Radio 的真实编辑器渲染截图，并做 PIE 冒烟检查：真实角色正常生成、6 处证物冷光与 Lumen 设置在运行时存在。本次未重跑整套路线/对话流程。
> - 资料与地图修改前备份：`Saved/LightingRefine20261112/`，其中 `Backup/Lvl_TownBlock.umap` 为本轮前备份，`before.json` / `skylight_before.json` / `after.json` / `pie_check.json` 为读回记录；`Plaza_Before.png`、`Plaza_After_v1.png`、`Photo_After_v1.png`、`Notice_After_v1.png`、`Radio_After_v1.png` 为画面证据。旧桌面报告和对比图片仍为上一轮版本，本次未覆盖；Google Doc 未修改。
> - Diversion 本次仍未提交；`dv status` 启动 agent 超时，无法确认最新同步状态。

本文取代 `Docs/Unarchived-Lighting-Traversal-Handoff-2026-11-11.md`，以本文的状态为准。旧文保留，用来查冻结时的原貌和历史决策。原始需求全文见 `Saved\LightingPass20261112\Freeze_20261111_210547\Original_Request.txt`。

## 一句话状态

悬空平台已全部换成贴墙的建筑构件，五条路线都用真实输入走通，整条调查流程可以完成。黄昏微调已按用户要求做完。桌面交付和报告已整理，**等待用户在编辑器里做外观验收**。Diversion 未提交。

## 当前保存状态

- 主关卡：`/Game/Inarchived/Maps/Lvl_TownBlock`。1896 个 Actor，`dirty_maps=[]`，`dirty_content=[]`，PIE 已停止，编辑器保持打开。
- 分支：`codex/dialogue-pacing-2026-11-05`（over `dv.commit.15`）。本轮没有执行提交、合并或推送。
  - 本轮改动的工程文件只有两个：`Content/Inarchived/Maps/Lvl_TownBlock.umap` 和 `Content/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.uasset`（跳跃参数）。
  - `dv status` 里其他约 66 个路径是本任务开始前就有的改动，不要一并归到本任务。
- 备份（`Saved\LightingPass20261112\Backup_20261111_211800_PreWallRoutes\`）：
  - 根目录：贴墙改造前的地图、角色 BP，以及全量 Actor 清单 `inventory_before.json`。
  - `PreTextEdit\`：改文本前的角色 BP 和 `BP_TownQuestioner`。那次改动已还原，备份没有用上。
  - `PreDusk\`：黄昏微调前的地图，原灯光值另存在 `wallroute\dusk_before.json`。
- 更早的快照：`Freeze_20261111_210547\`（被否定的脚手架方案）、`Backup_20261111_195319\`（任务开始前）。**不要整目录覆盖恢复**，需要什么先逐个比对。

## 已完成内容

### 1. 平台（悬空 → 贴墙）
- **已删除**：
  - 五组 `TRV_Float_*`：49 块平台、3 面 LowWall、5 个 `*_Root`。
  - 被否定方案留下的 109 个 `LP_Photo_*` / `LP_Radio_*`。
  - 删除前确认过：这些 Actor 没有被任何 BP、关卡或配置引用。
- **新增**：367 个 `WR_<Route>_*` Actor，大纲视图文件夹为 `Traversal/WallRoutes/<Route>`，标签为 `WallRoute`；可踩的顶面另有标签 `WR_Walkable`。
- **碰撞规则**：
  - 可踩的顶面用 BlockAll。
  - 托架、牛腿、斜撑、垂边、龙骨用 NoCollision。
  - 栏杆有碰撞，但只放在外沿，不挡跳跃线。
  - 每个构件都单独追踪墙面，并嵌入墙内 2 cm。
- **五条路线**：

  | 路线 | 所在建筑 | 过程 | 终点物件 |
  |---|---|---|---|
  | Photo | House_NWBlock_01 | 楼梯平台 412 → 东立面：窗台 525、外凸砖 640、腰线 760、离墙 12 cm 的异常窗台 870 → 东北角木平台 980 → 北立面：楼板线 1105、檐口 1225 → 翻栏杆上屋顶 1240 → 南沿 belvedere 1345 | Photograph，未移动 |
  | Radio | House_AlleyE 巷侧 | 桥 550 → 托架板、窗遮雨棚、窗台、过于整齐的砖、检修板、檐口（660–1200）→ 屋顶 → 南沿木阳台 1300 | Radio，未移动 |
  | Alley | House_AlleyW 巷侧 | 桥 550 → 655–1160 六级，其中 970 那级窗台有轻微倾斜 → 屋顶 → 巷侧石阳台 1250 | Carbon Register，未移动 |
  | South | SS_03 / SS_05 夹缝 | 楼梯顶走道 710 → 两墙交替 815–1340 → SS_05 女儿墙下检修走道 1440 | Stopped Watch，Z 从 1522 降到 1452 |
  | East | House_NEBlockW_01 | 走廊花箱 665 → 跨过东南角的遮雨棚 775 → 东立面托架平台 885 → 东檐下瞭望阳台 995（朝向 The Guy） | Worn Key，从 (3000,270,1157) 移到 (3490,1430,1007) |

  East 路线另外补上了东走廊外栏原先留给悬空路线的 230 cm 缺口。

- **跳跃参数**：JumpZVelocity 500 → 600（跳高约 128 → 184 cm），AirControl 0.35 → 0.45，运行时读回一致。全图没有顶部落在 128–190 cm 之间的围墙或栏杆，也没有 BlockingVolume，跳得更高不会打开新的越界通道。

### 2. 灯光（当前值）
- **Sun**：Movable，俯仰 −8°、偏航 165°，强度 6.5，sRGB 颜色 (255,205,155)。
- **SkyLight**：Movable，强度 0.62，颜色 (218,224,255)，实时捕获。
- **场景里另有**：SkyAtmosphere、VolumetricCloud、ExponentialHeightFog（密度 0.018，偏粉紫的散射色）。这三项都没有改过。
- **PPV `WarmGrade`**：
  - Unbound、优先级 10。
  - 曝光：Manual，关闭物理相机曝光，Bias +0.45，无曲线；局部曝光为中性 1.0。
  - 调色：WhiteTemp 6100，饱和度 0.97，对比度 1.035，高光增益 (1.05,0.99,0.92)，阴影增益 (0.96,0.99,1.04)。
  - 其他：Bloom 0.15，Vignette 0.12，MotionBlur 0，GI 和反射都用 Lumen。
- **实用灯**：
  - Notice 18 cd。
  - Photo 24 cd，灯头在 1565。
  - Radio 12 cd，灯头在 1515。
  - 灯头抬到人物头顶以上，灯壳和镜片改成 NoCollision，以前用的裸灯杆已换成女儿墙上的灯柱。
  - 43 盏街灯：24 cd，半径 540。
- **参考球**：`LightingPass/Validation` 下的三个球，标签 CaptureOnly，游戏中隐藏，用于截图对比。

### 3. 测试（真实输入：AddMovementInput + Jump；E 键用 IA_Interact；对话选项用真实鼠标点击；没有瞬移）
- 五条路线都从出生点完整走通。
- 同一局内依次完成：
  - Notice
  - Photograph：选 B，证据数为 1；重复阅读仍为 1，`bLastAdded=False`
  - 原路下楼
  - Radio：选 A，证据数为 2；重复仍为 2
  - 原路下梯
  - The Guy：选 Leave，出现 END / LEAVE，`bPrototypeComplete=True`
- 其他确认项：
  - 三个可选记录按 E 都能打开对应对话。
  - Journal 换行正常。
  - PromptText 字号为 22（Photograph 和 Radio）。
  - 东走廊放了花箱之后仍可从头走到尾。
- 局限：以上是脚本驱动的真实输入，不是盲测；下楼只测了 Photo 和 Radio 两条路线。
- 日志位置：`Saved\LightingPass20261112\wallroute\tests\`。

### 4. 交付
桌面目录 `D:\某时之神社的双子猫娘\Unarchived_LightingPass_2026-11-12\`：

| 子目录 / 文件 | 内容 |
|---|---|
| `Lighting_Before_After\` | 4 组 Before / After / 左右对比图，全部为黄昏版。After 用 HighResShot 2208×1273 渲染，与 Before 的机位、取景完全一致，画面里有参考球 |
| `Original_Journal_Before\` | 11/05 的四张原图，未改动 |
| `Lighting_Setup\` | Environment_Lights、PostProcess_Settings（另有 ColorGrading、LocalExposure、Unbound 三张）、Reference_Spheres |
| `Traversal_Iteration\` | Before、After、对比图、被否定的中间方案截图、7 张路线细节图、8 张照片路线游戏内落点截图 |
| `Game_System\` | Evidence_Interaction（END / LEAVE）、两张选项面板截图、三张可选记录交互截图 |
| `Implementation_Report.txt`、`GoogleDoc_Captions.txt` | 报告和可直接粘贴的文案。工程内副本在 `wallroute\delivery_copy\` |

注意：PostProcess_Settings 截图是黄昏微调前拍的（Bias 显示 0.3），报告里已注明。Google Doc 没有动，需要用户自己粘贴。

## 未完成 / 待处理（按优先级）

1. **用户验收**：在编辑器和游戏里看一遍五条路线的外观，确认“贴墙、融入建筑”这个要求达到了。上一版正是在这一点上被否定的。
2. **HUD 和台词里还有旧说法**：
   - `BP_ThirdPersonCharacter` > RefreshJournal 中最后一个 `SetText(JournalGoal)`（节点 `701AECA9`）写着 “Seek the PHOTO and RADIO above the floating routes”。
   - `BP_TownQuestioner` > Talk 里写着 “Follow the floating routes above the north streets”。
   - Bridge 的 `unreal_set_pin_default_value` 只能写 DefaultValue，写不进 FText 字面量（试过一次，已还原）。需要在编辑器里手动改，建议改成 “…the PHOTO and RADIO up on the rooftops”。
3. Photograph 和 Radio 的 “E - Inspect” 世界文字朝北，从阳台那一侧看是镜像的。把这两个实例上的 PromptText 组件转 180° 即可。
4. 原有问题：南走廊外栏横跨在 `TRV_SouthFront_Stair_02` 楼梯口上，去 South 路线时得先跳过这道栏杆。
5. 如果用户要求，重拍 PostProcess_Settings，以反映 Bias 0.45。
6. Google Doc 11/12 页签 `t.qeetsadecfvq`：按 `GoogleDoc_Captions.txt` 插入图片和文字，不要动 11/05 页签。
7. 在用户同意之后再执行 `dv commit`。提交前先 `dv diff`，只纳入本任务的改动。

## 工具与复现入口（`Saved\LightingPass20261112\wallroute\`）

- **调用方式**：`run.ps1 <script.py>` 通过 `..\mcp.mjs python exec` 在编辑器内执行（unreal-mcpython，TCP 12029）。Bridge（8765）用于截图和 BP 工具；official MCP 在 `127.0.0.1:8000`，用于 Slate。**UE 操作必须串行执行。**
- **路线（核心）**：
  - `routes.py`：五条路线的构件数据和路径，唯一的数据源。
  - `validate.py`：离线检查净空、头顶空间和抛物线碰撞。
  - `build_wall_routes.py`：在 `wr_request.json` 里填 `{"route":"Photo","delete_old":true}`，按路线幂等重建；先删掉自己的 `WR_<Route>_*` 再生成，并负责移动记录、调整灯头。
- **测试**：
  - `gen_pilot.py <Route> full`：生成 `pilot_request.json`，内含从出生点出发的接近路线。
  - `pie.py`：配合 `pie_cmd.json` 使用 start、stop、probe。
  - `pilot2.py`：实际操控角色，结果写到 `tests\<name>.json`。
  - `poll.ps1 <name> <秒>`：等待测试结果。
- **交互**：
  - `act.ps1 press|state|choose|snap`：按 E、读取状态、通过 Slate 点击、截快照。
  - 注意：Slate 点击 UMG 按钮不会触发 OnClicked，对话选项要用 Computer Use 真实点击 PIE 视口。
- **截图**：
  - `shot.ps1`：编辑器视口截图。
  - `..\camera.py` 配合 `capture_request.json`：固定机位，同时摆好参考球。
  - `hires.py`：HighResShot 2208×1273。
  - `gameshot.py`：游戏内 Shot showui。
  - `spheres.py`：参考球的隐藏和恢复，`restore_play` 会顺带保存关卡。
  - `imgtools.ps1`：裁剪和左右拼图。
- **灯光**：`dusk_read.py` 读取当前值；`dusk_apply.py` 配合 `dusk_params.json` 应用参数。颜色按 sRGB 填写，脚本会转成线性。

## 踩过的坑

- `set_light_color` 收的是线性颜色，直接把 /255 的 sRGB 值传进去，颜色几乎不会变。
- 头部净空：跳跃顶点约 184 cm，加上胶囊高度，从起跳点算起上方约 364 cm 内不能有构件；同一面墙不要叠着放，要错开或绕到相邻墙面。
- 走廊和楼梯上方的构件，底面要比走道高出 195 cm 以上，否则会卡住路过的玩家。这次第一块窗台就因此在楼梯上把人卡住了。
- 东屋檐向外悬出约 50 cm，站立点要离墙 110 cm 以上。
- 记录 Actor 带碰撞，角色可能落在记录上，测试点要和它错开。
- 屋顶上有烟囱：AE 在 X 500–820，AW 在 X −550 到 −500。
- 导航网格没有构建，不能用 NavigationSystem 寻路。接近路线参考 `wallroute\town_map.txt` 和 `crop.py` 生成的高度图。
- `Shot showui` 会拍下整个编辑器窗口，需要裁剪视口区域 (0,155,1550,1320)。编辑器布局变化会改变视口比例，所以对比图统一用 HighResShot 固定分辨率。
- 不要运行旧目录里的 `implement.py`、`restore_route_spacing.py`、`fix_*.py`，它们会恢复已被否定的路线。
