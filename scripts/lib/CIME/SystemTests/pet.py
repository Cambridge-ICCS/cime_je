"""
Implementation of the CIME PET test.  This class inherits from SystemTestsCommon

This is an openmp test to determine that changing thread counts does not change answers.
(1) do an initial run where all components are threaded by default (suffix: base)
(2) do another initial run with nthrds=1 for all components (suffix: single_thread)
"""

from CIME.XML.standard_module_setup import *
from CIME.SystemTests.system_tests_compare_two import SystemTestsCompareTwo

logger = logging.getLogger(__name__)

class PET(SystemTestsCompareTwo):

    def __init__(self, case):
        """
        initialize a test object
        """
        SystemTestsCompareTwo.__init__(self, case,
                                       separate_builds = False,
                                       multisubmit=True,
                                       run_two_suffix = 'single_thread',
                                       run_one_description = 'default threading',
                                       run_two_description = 'threads set to 1')

    def _case_one_setup(self):
        # first make sure that all components have threaded settings
        comp_interface = self._case.get_value("COMP_INTERFACE")
        for comp in self._case.get_values("COMP_CLASSES"):
            if self._case.get_value("NTHRDS_{}".format(comp)) <= 1:
                self._case.set_value("NTHRDS_{}".format(comp), 2)
                # For nuopc we must also adjust the ROOTPE
                if comp_interface == 'nuopc':
                    rootpe = self._case.get_value("ROOTPE_{}".format(comp))
                    if rootpe > 0:
                        self._case.set_value("ROOTPE_{}".format(comp), rootpe + self._case.get_value("NTASKS_{}".format(comp)))



        # Need to redo case_setup because we may have changed the number of threads


    def _case_two_setup(self):
        #Do a run with all threads set to 1
        comp_interface = self._case.get_value("COMP_INTERFACE")
        for comp in self._case.get_values("COMP_CLASSES"):
            nthrds = self._case.get_value("NTHRDS_{}".format(comp))
            self._case.set_value("NTHRDS_{}".format(comp), 1)
            if comp_interface == 'nuopc':
                rootpe = self._case.get_value("ROOTPE_{}".format(comp))
                if rootpe > 0:
                    self._case.set_value("ROOTPE_{}".format(comp), rootpe//nthrds)


        # Need to redo case_setup because we may have changed the number of threads
        self._case.case_setup(reset=True, test_mode=True)
