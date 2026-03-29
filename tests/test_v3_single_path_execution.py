from experiment.phases.learning_helpers import apply_attention_update


class _UpdateOnlyAgent:
    def update(self, *_args, **_kwargs):
        return None


def test_v3_single_path_execution_rejects_legacy_update_dispatch():
    try:
        apply_attention_update(_UpdateOnlyAgent(), state="s", reward=1.0, action=None)
        assert False, "Expected single-path execution guard to reject legacy update-only dispatch."
    except AttributeError as exc:
        assert "learn(Transition)" in str(exc)
