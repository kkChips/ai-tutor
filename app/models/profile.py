"""画像数据库模型 - MySQL存储

对照 ai_architecture_plan.md 的9维度画像定义
画像JSON整体存储在MySQL的JSON字段中，避免拆表
"""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, Float, Boolean, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ProfileModel(Base):
    """画像表 - 每个用户一条记录，画像数据以JSON存储"""
    __tablename__ = "profiles"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="用户ID")
    profile_json: Mapped[str] = mapped_column(Text, comment="画像JSON（9维度完整数据）")
    conversation_count: Mapped[int] = mapped_column(Integer, default=0, comment="对话轮次")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class QuestionModel(Base):
    """题库表 - 持久化存储所有题目（经典题+LLM生成题）

    对照 ai_architecture_plan.md Phase 4：
    - 经典题（classic=True）预建，免校验
    - LLM动态题（classic=False）经交叉验证后入库
    - 所有题目持久化，支持复用和统计
    """
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(128), primary_key=True, comment="题目ID")
    knowledge_point: Mapped[str] = mapped_column(String(64), index=True, comment="知识点ID")
    type: Mapped[str] = mapped_column(String(16), comment="题型: choice/judge/fill_blank/analysis/code")
    level: Mapped[int] = mapped_column(Integer, comment="难度等级: 1-3")
    difficulty: Mapped[int] = mapped_column(Integer, comment="难度系数: 1-5")
    description: Mapped[str] = mapped_column(Text, comment="题目描述")
    options_json: Mapped[str] = mapped_column(Text, default="[]", comment="选项JSON（选择题）")
    answer: Mapped[str] = mapped_column(Text, comment="答案")
    explanation: Mapped[str] = mapped_column(Text, comment="解析")
    starter_code: Mapped[str] = mapped_column(Text, default="", comment="起始代码（编程题）")
    test_cases_json: Mapped[str] = mapped_column(Text, default="[]", comment="测试用例JSON")
    classic: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否经典题")
    source: Mapped[str] = mapped_column(String(64), default="", comment="来源：LeetCode/教材/LLM生成")
    tags_json: Mapped[str] = mapped_column(Text, default="[]", comment="标签JSON")
    usage_count: Mapped[int] = mapped_column(Integer, default=0, comment="使用次数")
    correct_rate: Mapped[float] = mapped_column(Float, default=0.0, comment="正确率")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class AnswerRecordModel(Base):
    """答题记录表 - 追踪每道题的答题历史

    用途：
    - 连续正确/错误统计（驱动画像规则）
    - 难度阶梯升降级
    - 学习轨迹数据
    """
    __tablename__ = "answer_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, comment="用户ID")
    question_id: Mapped[str] = mapped_column(String(128), comment="题目ID")
    knowledge_point: Mapped[str] = mapped_column(String(64), comment="知识点ID")
    user_answer: Mapped[str] = mapped_column(Text, default="", comment="用户答案")
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否正确")
    time_spent: Mapped[int] = mapped_column(Integer, default=0, comment="答题耗时(秒)")
    level_at_question: Mapped[int] = mapped_column(Integer, default=1, comment="答题时的难度等级")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="答题时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class ProfileSnapshotModel(Base):
    """画像快照表 - 每次画像变更保存一份快照，支持学习成长轨迹展示"""
    __tablename__ = "profile_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, comment="用户ID")
    profile_json: Mapped[str] = mapped_column(Text, comment="快照时的画像JSON")
    change_reason: Mapped[str] = mapped_column(String(256), default="", comment="变更原因")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="快照时间")


class ConversationModel(Base):
    """对话表 - 存储对话历史"""
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, comment="用户ID")
    conversation_id: Mapped[str] = mapped_column(String(64), index=True, comment="对话ID")
    role: Mapped[str] = mapped_column(String(16), comment="角色: user/assistant/system")
    content: Mapped[str] = mapped_column(Text, comment="消息内容")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")


class CloudVideoModel(Base):
    """云视频表 - 持久化存储共享视频资源"""
    __tablename__ = "cloud_videos"

    video_id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="视频ID")
    title: Mapped[str] = mapped_column(String(256), comment="视频标题")
    url: Mapped[str] = mapped_column(Text, comment="视频链接")
    knowledge_point: Mapped[str] = mapped_column(String(64), index=True, comment="关联知识点")
    uploaded_by: Mapped[str] = mapped_column(String(64), default="", comment="上传者")
    rating: Mapped[float] = mapped_column(Float, default=0.0, comment="平均评分")
    rating_count: Mapped[int] = mapped_column(Integer, default=0, comment="评分人数")
    tags_json: Mapped[str] = mapped_column(Text, default="[]", comment="标签JSON")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")


class VideoRatingModel(Base):
    """视频评分表 - 记录每次评分详情"""
    __tablename__ = "video_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[str] = mapped_column(String(64), index=True, comment="视频ID")
    user_id: Mapped[str] = mapped_column(String(64), default="", comment="评分用户")
    rating: Mapped[int] = mapped_column(Integer, comment="评分1-5")
    tags_json: Mapped[str] = mapped_column(Text, default="[]", comment="评价标签JSON")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="评分时间")


class CodeTemplateModel(Base):
    """代码模板表 - 持久化存储预制代码库"""
    __tablename__ = "code_templates"

    id: Mapped[str] = mapped_column(String(128), primary_key=True, comment="模板ID")
    knowledge_point: Mapped[str] = mapped_column(String(64), index=True, comment="知识点ID")
    title: Mapped[str] = mapped_column(String(256), comment="模板标题")
    description: Mapped[str] = mapped_column(Text, default="", comment="模板描述")
    code: Mapped[str] = mapped_column(Text, comment="代码内容")
    test_cases_json: Mapped[str] = mapped_column(Text, default="[]", comment="测试用例JSON")
    difficulty: Mapped[int] = mapped_column(Integer, default=1, comment="难度1-5")
    blanks_json: Mapped[str] = mapped_column(Text, default="[]", comment="填空信息JSON")
    classic: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否预制模板")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")


class SharedCodeModel(Base):
    """共享代码表 - 代码小社区"""
    __tablename__ = "shared_codes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="代码ID")
    user_id: Mapped[str] = mapped_column(String(64), index=True, comment="分享用户ID")
    knowledge_point: Mapped[str] = mapped_column(String(64), index=True, comment="知识点ID")
    title: Mapped[str] = mapped_column(String(256), comment="代码标题")
    code: Mapped[str] = mapped_column(Text, comment="代码内容")
    rating: Mapped[float] = mapped_column(Float, default=0.0, comment="平均评分")
    rating_count: Mapped[int] = mapped_column(Integer, default=0, comment="评分人数")
    tags_json: Mapped[str] = mapped_column(Text, default="[]", comment="标签JSON")
    ai_review: Mapped[str] = mapped_column(Text, default="", comment="AI点评")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")


class SharedCodeRatingModel(Base):
    """共享代码评分表"""
    __tablename__ = "shared_code_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code_id: Mapped[str] = mapped_column(String(64), index=True, comment="代码ID")
    user_id: Mapped[str] = mapped_column(String(64), default="", comment="评分用户")
    rating: Mapped[int] = mapped_column(Integer, comment="评分1-5")
    tags_json: Mapped[str] = mapped_column(Text, default="[]", comment="评价标签JSON")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="评分时间")


class CodeEvolutionModel(Base):
    """代码进化轨迹表"""
    __tablename__ = "code_evolutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, comment="用户ID")
    knowledge_point: Mapped[str] = mapped_column(String(64), comment="知识点ID")
    template_id: Mapped[str] = mapped_column(String(128), default="", comment="模板ID")
    iteration: Mapped[int] = mapped_column(Integer, comment="迭代次数")
    code: Mapped[str] = mapped_column(Text, comment="代码内容")
    status: Mapped[str] = mapped_column(String(32), comment="状态: syntax_error/runtime_error/logic_error/passed/optimized")
    error_message: Mapped[str] = mapped_column(Text, default="", comment="错误信息")
    test_results_json: Mapped[str] = mapped_column(Text, default="[]", comment="测试结果JSON")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")


class LearningActivityModel(Base):
    """学习活动记录表"""
    __tablename__ = "learning_activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, comment="用户ID")
    description: Mapped[str] = mapped_column(String(512), comment="活动描述")
    activity_type: Mapped[str] = mapped_column(String(32), comment="活动类型: code/share/question/etc")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")


class ResourceModel(Base):
    """资源表 - 所有Agent生成的资源持久化存储

    对照 AI开发指南_产品内核与架构规范.md 第6.2节：
    - 每生成一个资源，必须在数据库里记录它与知识图谱节点的关联
    - 这个关联关系是"动态触发资源"的基础
    """
    __tablename__ = "resources"

    id: Mapped[str] = mapped_column(String(128), primary_key=True, comment="资源ID")
    type: Mapped[str] = mapped_column(String(32), index=True, comment="资源类型: path/document/question/code/video/mind_map/assessment/reading")
    content_json: Mapped[str] = mapped_column(Text, comment="资源内容JSON")
    kg_node_ids: Mapped[str] = mapped_column(Text, default="[]", comment="关联知识图谱节点ID列表(JSON数组)")
    path_node_id: Mapped[str] = mapped_column(String(128), default="", comment="关联学习路径节点")
    parent_resource_id: Mapped[str] = mapped_column(String(128), default="", comment="父资源ID")
    user_id: Mapped[str] = mapped_column(String(64), index=True, comment="所属用户ID")
    title: Mapped[str] = mapped_column(String(256), default="", comment="资源标题")
    status: Mapped[str] = mapped_column(String(32), default="completed", comment="状态")
    summary: Mapped[str] = mapped_column(String(512), default="", comment="摘要")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")


class KnowledgeNodeModel(Base):
    """知识节点表 - 知识图谱核心节点"""
    __tablename__ = "knowledge_nodes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="节点ID")
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="节点名称")
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="分类")
    description: Mapped[str] = mapped_column(String(512), default="", comment="描述")
    optional: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否可选")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class KnowledgeDependencyModel(Base):
    """知识依赖表 - 知识图谱节点间依赖关系"""
    __tablename__ = "knowledge_dependencies"
    __table_args__ = (
        UniqueConstraint("node_id", "dependency_id", name="uq_node_dependency"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    node_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_nodes.id"), nullable=False, comment="节点ID")
    dependency_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_nodes.id"), nullable=False, comment="依赖节点ID")


class KnowledgeContentModel(Base):
    """知识内容表 - 知识节点的多类型内容"""
    __tablename__ = "knowledge_content"
    __table_args__ = (
        UniqueConstraint("node_id", "content_type", name="uq_node_content_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    node_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_nodes.id"), nullable=False, comment="节点ID")
    content_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="内容类型: concept/principle/code_example/common_mistake/applications/summary")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="内容")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class KnowledgeAliasModel(Base):
    """知识别名表 - 知识节点的别名/同义词"""
    __tablename__ = "knowledge_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alias: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, comment="别名")
    node_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_nodes.id"), nullable=False, index=True, comment="节点ID")


class VideoTemplateModel(Base):
    """视频模板表 - 知识点关联的视频模板"""
    __tablename__ = "video_templates"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="模板ID")
    node_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_nodes.id"), nullable=False, index=True, comment="节点ID")
    scene_class: Mapped[str] = mapped_column(String(128), nullable=False, comment="场景类")
    script: Mapped[str] = mapped_column(Text, nullable=False, comment="脚本")
    narrations_json: Mapped[str] = mapped_column(Text, default="", comment="旁白JSON")
    duration_estimate: Mapped[int] = mapped_column(Integer, default=90, comment="预估时长(秒)")
    difficulty: Mapped[int] = mapped_column(Integer, default=1, comment="难度1-5")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否默认模板")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class VisualizationConfigModel(Base):
    """可视化配置表 - 知识点关联的可视化配置"""
    __tablename__ = "visualization_configs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="配置ID")
    node_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_nodes.id"), nullable=False, index=True, comment="节点ID")
    component_type: Mapped[str] = mapped_column(String(32), nullable=False, comment="组件类型")
    data_schema_json: Mapped[str] = mapped_column(Text, default="", comment="数据Schema JSON")
    controls_json: Mapped[str] = mapped_column(Text, default="", comment="控件JSON")
    step_templates_json: Mapped[str] = mapped_column(Text, default="", comment="步骤模板JSON")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class AchievementModel(Base):
    """成就表 - 成就定义"""
    __tablename__ = "achievements"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="成就ID")
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="成就名称")
    description: Mapped[str] = mapped_column(String(512), default="", comment="描述")
    icon: Mapped[str] = mapped_column(String(32), default="🏆", comment="图标")
    category: Mapped[str] = mapped_column(String(32), default="", comment="分类")
    condition_json: Mapped[str] = mapped_column(Text, default="", comment="达成条件JSON")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")


class UserAchievementModel(Base):
    """用户成就表 - 用户达成成就记录"""
    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="用户ID")
    achievement_id: Mapped[str] = mapped_column(String(64), ForeignKey("achievements.id"), nullable=False, comment="成就ID")
    progress: Mapped[float] = mapped_column(Float, default=0.0, comment="进度")
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, comment="解锁时间")


class SourceReferenceModel(Base):
    """来源参考表 - 知识节点的参考来源"""
    __tablename__ = "source_references"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    node_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_nodes.id"), nullable=False, comment="节点ID")
    source_type: Mapped[str] = mapped_column(String(32), default="", comment="来源类型")
    title: Mapped[str] = mapped_column(String(256), nullable=False, comment="标题")
    detail: Mapped[str] = mapped_column(String(512), default="", comment="详情")
    url: Mapped[str] = mapped_column(String(512), default="", comment="链接")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")


class ProfileKnowledgeMasteryModel(Base):
    """用户知识掌握度表 - 用户对知识节点的掌握情况"""
    __tablename__ = "profile_knowledge_mastery"
    __table_args__ = (
        UniqueConstraint("user_id", "node_id", name="uq_user_node_mastery"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="用户ID")
    node_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="节点ID")
    mastery: Mapped[float] = mapped_column(Float, default=0.0, comment="掌握度")
    times_learned: Mapped[int] = mapped_column(Integer, default=0, comment="学习次数")
    last_learned_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, comment="最后学习时间")
    last_reviewed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, comment="最后复习时间")
    strength: Mapped[float] = mapped_column(Float, default=1.0, comment="记忆强度")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class LearningPathModel(Base):
    """学习路径表 - 用户的学习路径"""
    __tablename__ = "learning_paths"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, comment="路径ID")
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="用户ID")
    title: Mapped[str] = mapped_column(String(256), nullable=False, comment="路径标题")
    strategy: Mapped[str] = mapped_column(String(32), default="", comment="策略")
    total_nodes: Mapped[int] = mapped_column(Integer, default=0, comment="总节点数")
    completed_nodes: Mapped[int] = mapped_column(Integer, default=0, comment="已完成节点数")
    status: Mapped[str] = mapped_column(String(32), default="active", comment="状态")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class LearningPathNodeModel(Base):
    """学习路径节点表 - 路径中的知识节点"""
    __tablename__ = "learning_path_nodes"

    id: Mapped[str] = mapped_column(String(128), primary_key=True, comment="路径节点ID")
    path_id: Mapped[str] = mapped_column(String(64), ForeignKey("learning_paths.id"), nullable=False, index=True, comment="路径ID")
    node_id: Mapped[str] = mapped_column(String(64), ForeignKey("knowledge_nodes.id"), nullable=False, comment="知识节点ID")
    phase_name: Mapped[str] = mapped_column(String(128), default="", comment="阶段名称")
    day_number: Mapped[int] = mapped_column(Integer, default=1, comment="天数")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    status: Mapped[str] = mapped_column(String(32), default="pending", comment="状态")
    estimated_hours: Mapped[float] = mapped_column(Float, default=1.0, comment="预估学时")
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, comment="开始时间")
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, comment="完成时间")
