"""
Message classes for CIE UI components.
"""

from textual.message import Message

from cie.core.models import Policy, Trial


class OptimizerRunMessage(Message):
    """Message sent when an optimizer proposes a new policy."""

    def __init__(self, policy: Policy) -> None:
        self.policy = policy
        super().__init__()


class EvalRunMessage(Message):
    """Message sent when an evaluation completes."""

    def __init__(self, trial: Trial) -> None:
        self.trial = trial
        super().__init__()


class PolicyAdoptedMessage(Message):
    """Message sent when a policy is adopted."""

    def __init__(self, trial_id: int, success: bool) -> None:
        self.trial_id = trial_id
        self.success = success
        super().__init__()


class ConfigUpdatedMessage(Message):
    """Message sent when configuration is updated."""

    def __init__(self, config_data: dict) -> None:
        self.config_data = config_data
        super().__init__()


class WeightsUpdatedMessage(Message):
    """Message sent when objective weights are updated."""

    def __init__(self, weights: dict) -> None:
        self.weights = weights
        super().__init__()


class PanelMaximizedMessage(Message):
    """Message sent when a panel is maximized."""

    def __init__(self, panel_id: str) -> None:
        self.panel_id = panel_id
        super().__init__()


class PanelMinimizedMessage(Message):
    """Message sent when a panel is minimized."""

    def __init__(self, panel_id: str) -> None:
        self.panel_id = panel_id
        super().__init__()


class ExperimentStartedMessage(Message):
    """Message sent when an experiment is started."""

    def __init__(self, experiment_id: str, optimizer_id: int, workload_id: int) -> None:
        self.experiment_id = experiment_id
        self.optimizer_id = optimizer_id
        self.workload_id = workload_id
        super().__init__()


class ExperimentCompletedMessage(Message):
    """Message sent when an experiment completes."""

    def __init__(self, experiment_id: str, best_trial: Trial) -> None:
        self.experiment_id = experiment_id
        self.best_trial = best_trial
        super().__init__()


class RefreshRequestedMessage(Message):
    """Message sent when a refresh is requested."""

    def __init__(self, component: str = "all") -> None:
        self.component = component
        super().__init__()


class ErrorMessage(Message):
    """Message sent when an error occurs."""

    def __init__(self, error: str, component: str = "") -> None:
        self.error = error
        self.component = component
        super().__init__()


class WarningMessage(Message):
    """Message sent when a warning occurs."""

    def __init__(self, warning: str, component: str = "") -> None:
        self.warning = warning
        self.component = component
        super().__init__()


class InfoMessage(Message):
    """Message sent for informational purposes."""

    def __init__(self, info: str, component: str = "") -> None:
        self.info = info
        self.component = component
        super().__init__()


class BackendConnectedMessage(Message):
    """Message sent when backend connection is established."""

    def __init__(self, backend_info: dict) -> None:
        self.backend_info = backend_info
        super().__init__()


class BackendDisconnectedMessage(Message):
    """Message sent when backend connection is lost."""

    def __init__(self, reason: str = "") -> None:
        self.reason = reason
        super().__init__()


class MetricsUpdatedMessage(Message):
    """Message sent when metrics are updated."""

    def __init__(self, metrics: dict, source: str = "") -> None:
        self.metrics = metrics
        self.source = source
        super().__init__()


class WorkloadChangedMessage(Message):
    """Message sent when workload selection changes."""

    def __init__(self, workload_id: int, workload_name: str) -> None:
        self.workload_id = workload_id
        self.workload_name = workload_name
        super().__init__()


class OptimizerChangedMessage(Message):
    """Message sent when optimizer selection changes."""

    def __init__(self, optimizer_id: int, optimizer_name: str) -> None:
        self.optimizer_id = optimizer_id
        self.optimizer_name = optimizer_name
        super().__init__()


class TrialSelectedMessage(Message):
    """Message sent when a trial is selected."""

    def __init__(self, trial_id: int) -> None:
        self.trial_id = trial_id
        super().__init__()


class ParetoUpdatedMessage(Message):
    """Message sent when Pareto frontier is updated."""

    def __init__(self, pareto_trials: list) -> None:
        self.pareto_trials = pareto_trials
        super().__init__()


class StorageUpdatedMessage(Message):
    """Message sent when storage backend is updated."""

    def __init__(self, storage_type: str, storage_info: dict) -> None:
        self.storage_type = storage_type
        self.storage_info = storage_info
        super().__init__()


class ModelProviderChangedMessage(Message):
    """Message sent when model provider is changed."""

    def __init__(self, provider: str, model_name: str) -> None:
        self.provider = provider
        self.model_name = model_name
        super().__init__()


class HelpRequestedMessage(Message):
    """Message sent when help is requested."""

    def __init__(self, help_topic: str = "general") -> None:
        self.help_topic = help_topic
        super().__init__()


class QuitRequestedMessage(Message):
    """Message sent when quit is requested."""

    def __init__(self, confirm: bool = False) -> None:
        self.confirm = confirm
        super().__init__()


# Panel-specific messages
class OptimizersPanel:
    """Messages for OptimizersPanel."""

    class OptimizerRun(Message):
        """Message sent when optimizer run is requested."""

        def __init__(self, policy: Policy) -> None:
            self.policy = policy
            super().__init__()


class EvalsPanel:
    """Messages for EvalsPanel."""

    class EvalRun(Message):
        """Message sent when evaluation run is requested."""

        def __init__(self, trial: Trial) -> None:
            self.trial = trial
            super().__init__()


class ExperimentsPanel:
    """Messages for ExperimentsPanel."""

    class PolicyAdopted(Message):
        """Message sent when policy adoption is requested."""

        def __init__(self, trial_id: int, success: bool) -> None:
            self.trial_id = trial_id
            self.success = success
            super().__init__()


# Import at the end to avoid circular imports
