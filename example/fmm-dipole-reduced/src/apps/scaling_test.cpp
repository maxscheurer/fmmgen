#include "calculate.hpp"
#include "tree.hpp"
#include "utils.hpp"
#include <chrono>
#include <fstream>
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

  std::cout << "Scaling Test Parameters" << std::endl;
  std::cout << "-----------------------" << std::endl;
  std::cout << "Nparticles = " << Nparticles << std::endl;
  std::cout << "ncrit      = " << ncrit << std::endl;
  std::cout << "theta      = " << theta << std::endl;
  std::cout << "maxorder   = " << maxorder << std::endl;

  std::vector<double> F_exact(3 * Nparticles, 0.0);
  std::vector<Particle> particles;
  std::default_random_engine generator(0.0);
  std::uniform_real_distribution<double> distribution(-1, 1);

  double mux_total = 0.0;
  double muy_total = 0.0;
  double muz_total = 0.0;

  double *mu = new double[3*Nparticles];
  double *r = new double[3*Nparticles];

  for (size_t i = 0; i < Nparticles; i++) {
    double mux = distribution(generator);
    double muy = distribution(generator);
    double muz = distribution(generator);
    double x = distribution(generator);
    double y = distribution(generator);
    double z = distribution(generator);

    double mod = std::sqrt(mux*mux + muy*muy + muz*muz);

    mux /= mod;
    muy /= mod;
    muz /= mod;

    mux_total += mux;
    muy_total += muy;
    muz_total += muz;

    mu[3*i+0] = mux;
    mu[3*i+1] = muy;
    mu[3*i+2] = muz;

    Particle tmp(&r[3*i], &mu[3*i]);
    particles.push_back(tmp);
  }

  //std::cout << "\n\n\n" << std::endl;


  std::cout << "Direct\n------" << std::endl;
  Timer timer1;
  evaluate_direct(particles, F_exact, Nparticles);
  double t1 = timer1.elapsed();
  std::cout << "Time = " << t1 << std::endl;

  for (size_t order = 2; order < maxorder; order++) {
    std::cout << "Order " << order << "\n-------" << std::endl;
    std::vector<double> F_approx(3 * Nparticles, 0.0);

    auto root = Cell(0.0, 0.0, 0.0, 1.0, 0, order, 0, ncrit);
    auto cells = build_tree(particles, root, ncrit, order);
    std::vector<double> M(cells.size() * (Nterms(order) - Nterms(0)), 0.0);
    std::vector<double> L(cells.size() * Nterms(order - 1), 0.0);

    for(size_t i = 0; i < cells.size(); i++) {
      std::cout << "M size = " << Nterms(order) - Nterms(0) << std::endl;
      std::cout << "L size = " << Nterms(order - 1) << std::endl;
      cells[i].M = &M[i*(Nterms(order) - Nterms(0))];
      cells[i].L = &L[i*(Nterms(order - 1))];
    }
    // printTreeParticles(cells, 0, 0);

    std::cout << "Tree built with " << cells.size() << " cells.\n\n\n" << std::endl;

    //for(size_t i = 0; i < cells.size(); i++) {
    //  if (cells[i].nleaf < ncrit) {
    //	       std::cout << "leaf("<<i<<")"<<std::endl;
    //  }
    //}
    //std::cout << "\n\n\n" << std::endl;


    //for(size_t i = 0; i < cells.size(); i++) {
    //  std::cout << "cell["<<i<<"].nchild = " << cells[i].nchild << std::endl;
    // }
    Timer timer2;
    evaluate_P2M(particles, cells, 0, ncrit, order);
    //std::cout << "P2M - done" << std::endl;
    evaluate_M2M(particles, cells, order);

    // std::cout << "M2M - done" << std::endl;

    // std::cout << "cells.size() = " << cells.size() << std::endl;
    // std::cout << "cells[0].M.size() = " << cells[0].M.size() << std::endl;
    // for(size_t i = 0; i < cells.size(); i++) {
    //   std::cout << "M["<<i<<"] = ";
    //   size_t nterms = cells[i].M.size();
    //   for(size_t j = 0; j < nterms - 1; j++) {
    // 	std::cout << cells[i].M[j] << ", ";
    //   }
    //   std::cout << cells[i].M[nterms-1] << std::endl;
    // }

    interact_dehnen(0, 0, cells, particles, theta, order, ncrit, F_approx.data());
    evaluate_L2L(cells, order);
    evaluate_L2P(particles, cells, F_approx.data(), ncrit, order);

    double t2 = timer2.elapsed();
    double vrel_err = 0;
    double Exrel_err = 0;
    double Eyrel_err = 0;
    double Ezrel_err = 0;

    std::string filename = "error_order_" + std::to_string(order) + ".txt";
    std::ofstream fout(filename);
    for (size_t i = 0; i < particles.size(); i++) {
      double exerr =
	(F_exact[3 * i + 0] - F_approx[3 * i + 0]) / F_exact[3 * i + 0];
      double eyerr =
	(F_exact[3 * i + 1] - F_approx[3 * i + 1]) / F_exact[3 * i + 1];
      double ezerr =
	(F_exact[3 * i + 2] - F_approx[3 * i + 2]) / F_exact[3 * i + 2];

      fout << exerr << "," << eyerr << "," << ezerr << std::endl;
      Exrel_err += sqrt(exerr * exerr);
      Eyrel_err += sqrt(eyerr * eyerr);
      Ezrel_err += sqrt(ezerr * ezerr);
    }

    Exrel_err /= particles.size();
    Eyrel_err /= particles.size();
    Ezrel_err /= particles.size();

    std::cerr << "Rel errs = " << std::setw(10) << Exrel_err;
    std::cerr << ", " << std::setw(10) << Eyrel_err;
    std::cerr << ", " << std::setw(10) << Ezrel_err << std::endl;

    std::cout << "Approx. calculation  = " << t2 << " seconds. "
              << std::setw(10) << t2 / t1 * 100 << "% of direct time."
              << std::endl;


  }

  return 0;
}
