#!/usr/bin/python3

import pytest

from osbuild import testutil

STAGE_NAME = "org.osbuild.ovf"


# Prepare dataset containing good and bad API call parameters
@pytest.mark.parametrize("test_data, expected_err", [
    # Bad API parameters
    ({}, "'vmdk' is a required property"),
    ({"vmdk": 123}, "123 is not of type 'string'"),
    ({"vmdk": "imagename"}, "'imagename' does not match '[a-zA-Z0-9+_.-]+.vmdk'"),
    ({"vmdk": "imagename.vmdk", "vmware": {"os_type": 1}}, "is not of type 'string'"),
    ({"vmdk": "imagename.vmdk", "virtualbox": {"os_type": 1}}, "is not of type 'string'"),
    ({"vmdk": "imagename.vmdk", "virtualbox": {"mac_address": 1}}, "is not of type 'string'"),
    ({"vmdk": "imagename.vmdk", "virtualbox": {"mac_address": "1"}}, "'1' does not match '^[a-fA-F0-9]{12}$'"),
    # Good API parameters
    ({"vmdk": "imagename.vmdk"}, ""),
    ({"vmdk": "imagename.vmdk", "vmware": {"os_type": "OtherGuest"}, "virtualbox": {"os_type": "OtherGuest"}}, ""),
])
# This test validates only API calls using correct and incorrect queries
def test_schema_validation_ovf(stage_schema, test_data, expected_err):
    test_input = {
        "type": STAGE_NAME,
        "devices": {
            "device": {
                "path": "some-path",
            },
        },
        "options": {
        }
    }
    test_input["options"].update(test_data)
    res = stage_schema.validate(test_input)

    if expected_err == "":
        assert res.valid is True, f"err: {[e.as_dict() for e in res.errors]}"
    else:
        assert res.valid is False
        testutil.assert_jsonschema_error_contains(res, expected_err, expected_num_errs=1)


@pytest.mark.skipif(not testutil.has_executable("qemu-img"), reason="need qemu-img")
@pytest.mark.parametrize("test_opts, expected_substrings", [
    # Replacements
    ({"vmware": {"os_type": "my-vmware-os-type"}}, ["my-vmware-os-type"],),
    ({"virtualbox": {"os_type": "my-vbox-os-type"}}, ["my-vbox-os-type"],),
    ({"virtualbox": {"mac_address": "000000000000"}}, ["000000000000"],),
])
def test_ovf_default_template(tmp_path, stage_module, test_opts, expected_substrings):
    faked_vmdk_path = tmp_path / "some-image.vmdk"
    faked_vmdk_path.write_bytes(b"1234")

    opts = {
        "vmdk": faked_vmdk_path,
    }
    opts.update(test_opts)

    stage_module.main(opts, tmp_path)

    expected_template_path = tmp_path / "some-image.ovf"

    for substring in expected_substrings:
        assert substring in expected_template_path.read_text()


def test_ovf_vbox_mac_address_differs(stage_module):
    macs = [
        stage_module.vbox_mac_address({}),
        stage_module.vbox_mac_address({}),
    ]

    assert macs[0] != macs[1]
    assert all(m.startswith("080027") for m in macs)
    assert all(len(m) == 12 for m in macs)


def test_ovf_vbox_mac_address_options(stage_module):
    assert stage_module.vbox_mac_address({"virtualbox": {"mac_address": "000000000000"}}) == "000000000000"
