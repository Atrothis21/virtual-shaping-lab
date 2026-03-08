from pathlib import Path
import re


ATTENTION_EDITORS = [
    "attention_latent_inhibition_editor.jsx",
    "attention_learned_irrelevance_editor.jsx",
    "attention_hall_pearce_negative_transfer_editor.jsx",
    "attention_mackintosh_predictiveness_editor.jsx",
    "attention_pearce_hall_uncertainty_editor.jsx",
    "attention_rapid_reacquisition_editor.jsx",
    "attention_associability_shifts_editor.jsx",
]


def test_attention_presets_use_attention_config_strategy_contract():
    base = Path("virtual_shaping_lab/ui/js/react")
    allowed_names = {"mackintosh", "pearce_hall"}

    for filename in ATTENTION_EDITORS:
        content = (base / filename).read_text(encoding="utf-8")
        assert "attention_config" in content, f"{filename} must emit experiment.attention_config"
        # Avoid regression to legacy top-level experiment.attention payload map in attention presets.
        assert "      attention:" not in content, (
            f"{filename} should not emit legacy experiment.attention map; use attention_config"
        )
        name_match = re.search(r"attention_config\s*:\s*\{[^}]*name:\s*\"([^\"]+)\"", content, re.DOTALL)
        assert name_match, f"{filename} must specify attention_config.name"
        assert name_match.group(1) in allowed_names, (
            f"{filename} has unsupported attention_config.name '{name_match.group(1)}'"
        )
