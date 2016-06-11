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
import jmetal.experiments.Settings;
import jmetal.metaheuristics.ibea.IBEA;
import jmetal.operators.selection.BinaryTournament;
import jmetal.util.JMException;
import jmetal.util.comparators.FitnessComparator;

import java.util.HashMap;
import java.util.List;

import jmetal.core.Problem;

/**
 * Settings class of algorithm IBEA
 */
public class SPL_SettingsIBEA extends Settings {

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
    public SPL_SettingsIBEA(Problem p) {
        super(p.getName());

        problem_ = p;
        // Default experiments.settings

    } // IBEA_Settings
    

    public Algorithm configureASE2013(long maxRunTimeMS) throws JMException {

        populationSize_ = 300;
        archiveSize_ = 300;

        mutationProbability_ = 0.001;
        crossoverProbability_ = 0.05;

        Algorithm algorithm;
        Operator selection;
        Operator crossover;
        Operator mutation;

        HashMap parameters; // Operator parameters

        algorithm = new SATIBEA_IBEATimeLimited(problem_,maxRunTimeMS);

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
    }
    
    
    
    public Algorithm configureICSE15(long maxRunTimeMS, String fm, int numFeat, List<List<Integer>> constr) throws JMException {
        // The configureSATIBEA with time limitation

        populationSize_ = 300;
        archiveSize_ = 300;

        mutationProbability_ = 0.001;
        crossoverProbability_ = 0.05;

        Algorithm algorithm;
        Operator selection;
        Operator crossover;
        Operator mutation;

        HashMap parameters; // Operator parameters

        algorithm = new SATIBEA_IBEATimeLimited(problem_,maxRunTimeMS);

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
        mutation = new SATIBEA_NewMutation(parameters, fm,  numFeat, constr);

        /* Selection Operator */
        parameters = new HashMap();
        parameters.put("comparator", new FitnessComparator());
        selection = new BinaryTournament(parameters);

        // Add the operators to the algorithm
        algorithm.addOperator("crossover", crossover);
        algorithm.addOperator("mutation", mutation);
        algorithm.addOperator("selection", selection);

        return algorithm;
    }

    public Algorithm configureSATIBEA(int maxEvaluation, String fm, int numFeat, List<List<Integer>> constr) throws JMException {

        populationSize_ = 300;
        archiveSize_ = 300;
        maxEvaluations_ = maxEvaluation;

        mutationProbability_ = 0.001;
        crossoverProbability_ = 0.05;

        Algorithm algorithm;
        Operator selection;
        Operator crossover;
        Operator mutation;

        HashMap parameters; // Operator parameters

        algorithm = new IBEA(problem_);

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
        mutation = new SATIBEA_NewMutation(parameters, fm,  numFeat, constr);

        /* Selection Operator */
        parameters = new HashMap();
        parameters.put("comparator", new FitnessComparator());
        selection = new BinaryTournament(parameters);

        // Add the operators to the algorithm
        algorithm.addOperator("crossover", crossover);
        algorithm.addOperator("mutation", mutation);
        algorithm.addOperator("selection", selection);

        return algorithm;
    }

    public Algorithm configureICSE2013(int maxEvaluations_) throws JMException {

        populationSize_ = 100;
        //maxEvaluations_ = 1000;
        archiveSize_ = 100;

        mutationProbability_ = 0.05;
        crossoverProbability_ = 0.9;

        Algorithm algorithm;
        Operator selection;
        Operator crossover;
        Operator mutation;

        HashMap parameters; // Operator parameters

        algorithm = new IBEA(problem_);

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

    public Algorithm configureSIPIBEA(int maxEvaluations_) throws JMException {

        populationSize_ = 100;
        //maxEvaluations_ = 1000;
        archiveSize_ = 100;

        mutationProbability_ = 0.05;
        crossoverProbability_ = 0.9;

        Algorithm algorithm;
        Operator selection;
        Operator crossover;
        Operator mutation;

        HashMap parameters; // Operator parameters

        algorithm = new SIP_IBEA(problem_);

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

//    public Algorithm configureTest(int maxEvaluations_) throws JMException {
//
//        populationSize_ = 100;
//        //maxEvaluations_ = 1000;
//        archiveSize_ = 100;
//
//        mutationProbability_ = 0.05;
//        crossoverProbability_ = 0.9;
//
//        Algorithm algorithm;
//        Operator selection;
//        Operator crossover;
//        Operator mutation;
//
//        HashMap parameters; // Operator parameters
//
//        algorithm = new TT_I(problem_);
//
//        // Algorithm parameters
//        algorithm.setInputParameter("populationSize", populationSize_);
//        algorithm.setInputParameter("maxEvaluations", maxEvaluations_);
//        algorithm.setInputParameter("archiveSize", archiveSize_);
//
//        // Mutation and Crossover for Real codification
//        parameters = new HashMap();
//        parameters.put("probability", crossoverProbability_);
//        crossover = new SPL_SinglePointCrossover(parameters);
//
//        parameters = new HashMap();
//        parameters.put("probability", mutationProbability_);
//        mutation = new BitFlipMutation(parameters);
//
//        /* Selection Operator */
//        parameters = new HashMap();
//        parameters.put("comparator", new FitnessComparator());
//        selection = new BinaryTournament(parameters);
//
//        // Add the operators to the algorithm
//        algorithm.addOperator("crossover", crossover);
//        algorithm.addOperator("mutation", mutation);
//        algorithm.addOperator("selection", selection);
//
//        return algorithm;
//    } // configure

    /**
     * Configure IBEA with user-defined parameter experiments.settings
     *
     * @return A IBEA algorithm object
     * @throws jmetal.util.JMException
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

        algorithm = new IBEA(problem_);

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
