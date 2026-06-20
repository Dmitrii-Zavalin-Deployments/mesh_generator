# tests/test_base_interface.py
import pytest
import pkgutil
import importlib
import src.steps as steps
from interfaces.base_interface import StepInterface
from src.state.mesh_generator_state import SovereignContainer, GridState

class TestBaseInterface:
    """
    Architectural Quality Gate for StepInterface.
    Enforces structural, codebase-wide, and stateful pipeline contracts.
    """

    def test_framework_enforces_constitutional_restrictions(self):
        """
        [STRUCTURAL GATE] Verify that the StepInterface metatest infrastructure
        actively intercepts and blocks unauthorized method definitions at class declaration time.
        """
        # Explicit validation of the __init_subclass__ protection barrier.
        with pytest.raises(TypeError, match="CONSTITUTION VIOLATION"):
            class RogueStep(StepInterface):
                def execute(self, container):
                    pass
                
                def unauthorized_helper_method(self):
                    """This method must trigger an immediate structural compilation failure."""
                    return True

    def test_all_production_steps_comply_with_constitution(self):
        """
        [STATIC ENFORCEMENT GATE] Dynamically discover, load, and scan every module 
        under 'src.steps/'. Ensures no hidden logic or rogue methods have been 
        introduced into the production pipeline execution path.
        """
        discovered_modules = list(pkgutil.iter_modules(steps.__path__))
        
        # Enforce that the pipeline directory is populated and readable
        assert len(discovered_modules) > 0, "Architectural Error: No steps found under src/steps/."

        for _, module_name, _ in discovered_modules:
            try:
                # Dynamic import triggers the __init_subclass__ hook for all classes inside the module.
                importlib.import_module(f"src.steps.{module_name}")
            except TypeError as error:
                pytest.fail(
                    f"CONSTITUTION VIOLATION: Production module 'src.steps.{module_name}' "
                    f"violates architectural restrictions: {error}"
                )

    def test_functional_state_mutation_contract(self):
        """
        [STATE TRACE GATE] Verify that a compliant implementation cleanly mutates
        the production SovereignContainer and interacts natively with nested types (GridState).
        """
        # 1. Setup: Construct a pristine production container with no mock components.
        container = SovereignContainer(
            step_file="test_geometry.step",
            max_element_size=1.5,
            solver_version="1.0.0",
            tolerance=1e-5,
            min_element_size=0.1,
            boundary_map={"inlet": "dirichlet"}
        )

        # 2. Implement a compliant test worker verifying contract-bound transformations.
        class ConcreteMockResolutionStep(StepInterface):
            def execute(self, target_container: SovereignContainer):
                # Populate the explicit grid state using real system structures
                target_container.grid = GridState(
                    x_min=0.0, x_max=10.0,
                    y_min=0.0, y_max=10.0,
                    z_min=0.0, z_max=5.0,
                    nx=10, ny=10, nz=5
                )
                target_container.mask = [1, 0, 1, 1]

        # 3. Execution Phase
        step_executor = ConcreteMockResolutionStep()
        step_executor.execute(container)

        # 4. Deterministic Verification: Asset properties match real system layouts perfectly
        assert isinstance(container.grid, GridState), "Contract Broken: Container grid state type mismatch."
        assert container.grid.nx == 10, "Data Mutation Error: Voxel count (nx) did not persist."
        assert container.mask == [1, 0, 1, 1], "Data Mutation Error: Computational mask array mismatch."

    def test_base_interface_rejection_on_direct_invocation(self):
        """
        [ABSTRACT SECURITY GATE] Enforce that the abstract base StepInterface itself
        cannot be executed directly without concrete implementation overrides.
        """
        container = SovereignContainer(
            step_file="test.step", max_element_size=1.0, solver_version="1.0",
            tolerance=1e-5, min_element_size=0.1, boundary_map={}
        )
        
        abstract_step = StepInterface()
        with pytest.raises(NotImplementedError):
            abstract_step.execute(container)