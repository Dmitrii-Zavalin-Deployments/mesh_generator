# tests/signatures/state/state_factory_test_signature.py

class StateFactoryTestSignature:
    """
    Centralized signature for validating State construction and schema integrity.
    This replaces the redundant test_global_no_extra_fields found in individual files.
    """

    def test_schema_integrity_no_extra_fields(self):
        """
        Validates that the StateFactory only accepts fields explicitly 
        defined in the schema. Any field not in the whitelist must trigger
        a schema validation error.
        """
        raise NotImplementedError

    def test_schema_integrity_all_required_fields_present(self):
        """
        Validates that the StateFactory enforces the No-Defaults Policy 
        by rejecting partial data inputs.
        """
        raise NotImplementedError