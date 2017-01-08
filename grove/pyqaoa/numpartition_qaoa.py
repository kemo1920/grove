import numpy as np
from pyquil.paulis import PauliTerm, PauliSum
import pyquil.forest as qvm_module
from scipy.optimize import minimize
from grove.pyqaoa.qaoa import QAOA
CXN = qvm_module.Connection()


def numpart_qaoa(asset_list, A=1.0, minimizer_kwargs=None, steps=1):
    """
    generate number partition driver and cost functions

    :param asset_list: list to binary parition
    :param A: (float) optional constant for level separation. Default=1.
    :param steps: (int) number of steps approximating the solution.
    """
    cost_operators = []
    ref_operators = []
    for ii in xrange(len(asset_list)):
        for jj in xrange(ii + 1, len(asset_list)):
            cost_operators.append(PauliSum([PauliTerm("Z", ii, 2*asset_list[ii]) *
                                            PauliTerm("Z", jj, A*asset_list[jj])]))
        ref_operators.append(PauliSum([PauliTerm("X", ii, -1.0)]))

    cost_operators.append(PauliSum([PauliTerm("I", 0, len(asset_list))]))

    if minimizer_kwargs is None:
        minimizer_kwargs = {'method': 'Nelder-Mead',
                            'options': {'ftol': 1.0e-2,
                                        'xtol': 1.0e-2,
                                        'disp': True}}
    n_qubits = len(asset_list)
    qaoa_inst = QAOA(CXN, n_qubits, steps=steps, cost_ham=cost_operators,
                     ref_hamiltonian=ref_operators, store_basis=True,
                     minimizer=minimize, minimizer_kwargs=minimizer_kwargs,
                     vqe_options={'disp': True})

    return qaoa_inst


if __name__ == "__main__":
    # Sample Run.
    # result should be an even partition of nodes
    inst = numpart_qaoa([1, 1, 1, 1, 1, 1], A=1.0, steps=1)
    betas, gammas = inst.get_angles()
    print betas
    print gammas
    probs = inst.probabilities(np.hstack((betas, gammas)))
    for state, prob in zip(inst.states, probs):
        print state, prob

    print "Most frequent bitstring from sampling"
    most_freq_string, sampling_results = inst.get_string(
            betas, gammas, samples=100)
    print most_freq_string