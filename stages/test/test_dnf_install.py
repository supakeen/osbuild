#!/usr/bin/env python3
import pytest

from osbuild import testutil

STAGE_NAME = "org.osbuild.dnf.install"


@pytest.mark.parametrize(
    "test_data,expected_err",
    [
        # good
        (
            {
                "actions": {"installs": [{"specs": ["a"]}]},
                "repositories": [{"id": "1", "path": "1"}],
            },
            "",
        ),
        (
            {
                "actions": {"installs": [{"specs": ["a"]}]},
                "repositories": [{"id": "1", "path": "1"}],
            },
            "",
        ),
    ],
)
def test_dnf_install_schema_validation(stage_schema, test_data, expected_err):
    test_input = {
        "type": STAGE_NAME,
        "options": {},
    }
    test_input["options"].update(test_data)
    res = stage_schema.validate(test_input)

    if expected_err == "":
        assert res.valid is True, f"err: {[e.as_dict() for e in res.errors]}"
    else:
        assert res.valid is False
        testutil.assert_jsonschema_error_contains(
            res, expected_err, expected_num_errs=1
        )
