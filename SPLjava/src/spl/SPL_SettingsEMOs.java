/*
 * Author : Christopher Henard (christopher.henard@uni.lu)
 * Date : 01/03/14
 * Copyright 2013 University of Luxembourg – Interdisciplinary Centre for Security Reliability and Trust (SnT)
 * All rights reserved
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.

 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.

 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
package spl;

import jmetal.core.Algorithm;
import jmetal.core.Operator;
import jmetal.core.Problem;
import jmetal.experiments.Settings;
import jmetal.metaheuristics.nsgaII.NSGAII;
import jmetal.metaheuristics.spea2.SPEA2;
import jmetal.operators.selection.BinaryTournament;
import jmetal.util.JMException;
import jmetal.util.comparators.FitnessComparator;

import java.util.HashMap;

/**
 * Settings class of algorithm NSGA-II , SPEA2 and MOEA/D
 */
public class SPL_SettingsEMOs extends Settings {

    public int populationSize_;
    public int maxEvaluations_;
    public int archiveSize_;

    public double mutationProbability_;
    public double crossoverProbability_;

    public double crossoverDistributionIndex_;
    public double mutationDistributionIndex_;

    /**
     * Constructor
     */
    public SPL_SettingsEMOs(Problem p) {
        super(p.getName());

        problem_ = p;
        // Default experiments.settings

    } // EMO_Settings



    public Algorithm configureNSGA2(int maxEvaluations_) throws JMException {

        populationSize_ = 100;
        this.maxEvaluations_ = maxEvaluations_;
        archiveSize_ = 100;

        mutationProbability_ = 0.05;
        crossoverProbability_ = 0.9;

        Algorithm algorithm;
        Operator selection;
        Operator crossover;
        Operator mutation;

        HashMap parameters; // Operator parameters

        algorithm = new NSGAII(problem_);

        // Algorithm parameters
        algorithm.setInputParameter("populationSize", populationSize_);
        algorithm.setInputParameter("maxEvaluations", maxEvaluations_);

        // Mutation and Crossover for Real codification
        parameters = new HashMap();
        parameters.put("probability", crossoverProbability_);
        crossover = new SPL_SinglePointCrossover(parameters);

        parameters = new HashMap();
        parameters.put("probability", mutationProbability_);
        mutation = new BitFlipMutation(parameters);

        /* Selection Operator */
        parameters = new HashMap();
        parameters.put("comparator", new FitnessComparator());
        selection = new BinaryTournament(parameters);

        // Add the operators to the algorithm
        algorithm.addOperator("crossover", crossover);
        algorithm.addOperator("mutation", mutation);
        algorithm.addOperator("selection", selection);

        return algorithm;
    } // configure


    public Algorithm configureSPEA2(int maxEvaluations_) throws JMException {

        populationSize_ = 100;
        archiveSize_ = 100;

        mutationProbability_ = 0.05;
        crossoverProbability_ = 0.9;

        Algorithm algorithm;
        Operator selection;
        Operator crossover;
        Operator mutation;

        HashMap parameters; // Operator parameters

        algorithm = new SPEA2(problem_);

        // Algorithm parameters
        algorithm.setInputParameter("populationSize", populationSize_);
        algorithm.setInputParameter("maxEvaluations", maxEvaluations_);
        algorithm.setInputParameter("archiveSize", archiveSize_);

        // Mutation and Crossover for Real codification
        parameters = new HashMap();
        parameters.put("probability", crossoverProbability_);
        crossover = new SPL_SinglePointCrossover(parameters);

        parameters = new HashMap();
        parameters.put("probability", mutationProbability_);
        mutation = new BitFlipMutation(parameters);

        /* Selection Operator */
        parameters = new HashMap();
        parameters.put("comparator", new FitnessComparator());
        selection = new BinaryTournament(parameters);

        // Add the operators to the algorithm
        algorithm.addOperator("crossover", crossover);
        algorithm.addOperator("mutation", mutation);
        algorithm.addOperator("selection", selection);

        return algorithm;
    } // configure



    /**
     * Configure NSGA2 with user-defined parameter experiments.settings
     * DO NOT USE THIS. Use configureNSGA2() instead
     *
     * @return A IBEA algorithm object
     * @throws JMException
     */
    public Algorithm configure() throws JMException {
        Algorithm algorithm;
        Operator selection;
        Operator crossover;
        Operator mutation;

        populationSize_ = 100;
        maxEvaluations_ = 1000;
        archiveSize_ = 100;

        mutationProbability_ = 0.05;
        crossoverProbability_ = 0.9;

        HashMap parameters; // Operator parameters

        algorithm = new NSGAII(problem_);

        // Algorithm parameters
        algorithm.setInputParameter("populationSize", populationSize_);
        algorithm.setInputParameter("maxEvaluations", maxEvaluations_);
        algorithm.setInputParameter("archiveSize", archiveSize_);

        // Mutation and Crossover for Real codification
        parameters = new HashMap();
        parameters.put("probability", crossoverProbability_);
        crossover = new SPL_SinglePointCrossover(parameters);

        parameters = new HashMap();
        parameters.put("probability", mutationProbability_);
        mutation = new BitFlipMutation(parameters);

        /* Selection Operator */
        parameters = new HashMap();
        parameters.put("comparator", new FitnessComparator());
        selection = new BinaryTournament(parameters);

        // Add the operators to the algorithm
        algorithm.addOperator("crossover", crossover);
        algorithm.addOperator("mutation", mutation);
        algorithm.addOperator("selection", selection);

        return algorithm;
    } // configure

} // IBEA_Settings
