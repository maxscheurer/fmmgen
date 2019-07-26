#include "calculate.hpp"
#include "tree.hpp"
#include "utils.hpp"
#include "operators.h"
#include "omp.h"
#include <chrono>
#include <fstream>
#include <algorithm>
#include <iomanip>
#include <iostream>
#include <random>
#include <string>

int main(int argc, char **argv) {
  // Set initial parameters by user input from
  // the command line:
  size_t Nparticles = std::stoul(argv[1]);
  size_t ncrit = std::stoul(argv[2]);
  double theta = std::stod(argv[3]);
  size_t maxorder = std::stoul(argv[4]);
  size_t type = std::stoul(argv[5]); // type == 0, FMM, type == 1, BH
  const size_t minorder = 2;
  const size_t calc_direct = 1;
	  
  std::cout << "Scaling Test Parameters" << std::endl;
  std::cout << "-----------------------" << std::endl;
  std::cout << "Nparticles = " << Nparticles << std::endl;
  std::cout << "ncrit      = " << ncrit << std::endl;
  std::cout << "theta      = " << theta << std::endl;
  std::cout << "maxorder   = " << maxorder << std::endl;

  std::vector<double> F_exact(Nparticles, 0.0);
  std::vector<double> F_approx(Nparticles, 0.0);
  std::default_random_engine generator(0.0);
  std::uniform_real_distribution<double> distribution(-1, 1);

  double mux_total = 0.0;
  double muy_total = 0.0;
  double muz_total = 0.0;

  // Array containing r and mu for faster memory access
  double *r = new double[3*Nparticles];
  double *mu = new double[3*Nparticles];

  for (size_t i = 0; i < Nparticles; i++) {
    double mux = distribution(generator);
    double muy = distribution(generator);
    double muz = distribution(generator);

    double mod = std::sqrt(mux*mux + muy*muy + muz*muz) * 1e24;
    mux /= mod;
    muy /= mod;
    muz /= mod;

    mux_total += mux;
    muy_total += muy;
    muz_total += muz;


    r[3*i+0] = distribution(generator) * 1e-9;
    r[3*i+1] = distribution(generator) * 1e-9;
    r[3*i+2] = distribution(generator) * 1e-9;
    mu[3*i+0] = mux;
    mu[3*i+1] = muy;
    mu[3*i+2] = muz;
  }

  double t_direct;
  double t_approx;

  for (size_t order = minorder; order < maxorder; order++) {
    Tree tree = build_tree(r, mu, Nparticles, ncrit, order, theta);
    std::cout << "Tree built with " << tree.cells.size() << " cells.\n\n\n" << std::endl;
    std::cout << "Order " << order << "\n-------" << std::endl;
    std::fill(F_approx.begin(), F_approx.end(), 0);
    if (order == minorder && calc_direct) {
      Timer timer;
      tree.compute_field_exact(&F_exact[0]);
      t_direct = timer.elapsed();
      std::cout << "t_direct = " << t_direct << std::endl;
    }
    Timer timer;
    if (type == 0) {
	tree.compute_field_fmm(&F_approx[0]);
    }
    else if (type == 1) {
	tree.compute_field_bh(&F_approx[0]);
    }
    t_approx = timer.elapsed();

    if (calc_direct) {
        double Potrel_err = 0;
        auto filename = "errors_lazy_p_" + std::to_string(order) +
                               "_n_" + std::to_string(Nparticles) +
                               "_ncrit_" + std::to_string(ncrit) +
                               "_theta_" + std::to_string(theta) + 
    			   "_type_" + std::to_string(type) + ".txt";
        std::ofstream fout(filename);
        for (size_t i = 0; i < Nparticles; i++) {
          double poterr = (F_exact[i] - F_approx[i]) / F_exact[i];
          fout << poterr << std::endl;
          Potrel_err += sqrt(poterr * poterr);
        }
        Potrel_err /= Nparticles;
        std::cerr << "Rel errs = " << std::scientific << std::setw(10) << Potrel_err << std::endl;

    }
    std::cout << "Approx. calculation  = " << t_approx << " seconds. " << std::endl;
    if (calc_direct) {
	    std:: cout << std::setw(10) << t_approx / t_direct * 100 << "% of direct time."
  	    << std::endl;
    }

  	
  }

  delete[] r;
  delete[] mu;
  return 0;
}
