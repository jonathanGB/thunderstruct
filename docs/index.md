# Abstract

Fractal growth is a comutationally intensive simulation which has typically ignored traditionoal first principles in physics in order to increase speed. Lightning is a well understood phenomena that can be simulated accurately with the Dielectric Breakdown Model, but it is computationally expensive to do so. We seek to optimize this simulation with HPC through the parallelization of the simualtion at each time step using a multi-node architecture on Google Cloud Engine. Using this approach, we obtained a non-trivial speedup and amanged to simulate lightning growth on a 1500x1500 grid.


# Description of problem and the need for HPC and/or Big Data

Fractal growth is a common natural phenomena; from the growth of blood vessels to the dispersion of electricity via lightning, the pattern is seen across disciplines. Given their commonplace naurre, the driving forces behind many of these processes are well understood. In particular, first-principles in physics dictate the flow of electricity in lightning with a high-level of accurracy. Yet, the models used to simulate its growth suffer from both inherent model-based flaws, as well as computational processing limits. 

In order to accurately simulate lightning based on first-principles, the Dielectric Breakdown Model is used. In this method, the charge distribution over a given grid is calculated by solving the Poisson equation. However, solving this partial differential equation is compuataionally expensive, requiring an expansion of the grid used. In order to solve for the growth at each time step on a 100 x 100 grid, one must solve for the dot product of a 10,000x10,000 matrix and a 10,000 element vector (or another square matrix). Obviously, this $O(N^2)$ scaling is inefficient but luckily matrix operations are easily parallelizable in theory. 


# Description of solution and comparison with existing work on the problem

Lightning is a form of electric discharge and grows in a fractal pattern. This occurs when there is a alarge enough chage between two objects. In many cases, and in the case of our simulations, this is the difference in a cloud of electrons and the ground. It begins with an initial negative charge distribution, the initial breakdown and then expands to another point, creating another breakdown. This extension from the initial breakdown to the point with the largest difference is known as the stepped leader. The entire process is quick; it only takes around 35ms (CITE). However, the process rapidly iterates with the negative charges of the first stepped leader laying the groundwork for subsequent bolts. Each bolt follows in the path of . the previous, albeit much faster (1-2ms) given the bias of the first stepped-leader. Moreover,  given the fractal pattern lightning ultimately achieves, it is classified as Laplacian growth. This is critical to much early work as Laplacian growth is a well understood concept and many approaches can yield accurate shapes. These two features of lightning, stepped leader behavior and laplacian growth, are the two primary targets of previous work in the area. 

In the past, lightning simulations  have been forced to choose between two paradigms: accurate models or efficient models. In accurate modeling, first-principles are used in order to more-accurately depict the growth of a lightning ray. However,  as mentioned above, this typically result in computationally slow models. On the other hand, lightning growth can be simulated for human observation simply by approximating the shape. These models are appealing to look at, and can grow quite large, but often lack any form of phyciscal principle: they are just fast and generate results that resemble lightning. 

## Diffusion Limited Aggregation (DLA)

![DLAout](figures/DLA.png)

To simulate only the shape, one possible appraoch is diffusion limited aggregation (DLA). In this method, there are five critical steps to understand:

1. A point charge is distributed randomly on a grid of an arbitrary size.
2. A second point is randomly chosen on the grid to begin a random walk. 
3. The second point is allowed to walk until it is within one grid-space of the initial charge.
4. With some probability $S$, the walker "sticks" to the charge. If it does not stick, it is allowed to continue to walk.
5. The process is repeated until the given number of "steps" (walks) have occurred.

Using the above method, one is able to accurately simulate the growth of fractal patterns and laplacian growth. The model is incredibly fast on small, two-dimension girds, as the computer must only randomly draw the direction of the random walk. This allows for rapid simulations compared to other methods, taking only (INSERT TIME).

However, the model breaks down in two critical ways: it scales poorly and it does not accurately simulate the shape of lightning (see below image). Given the model is essentially a series of random walks, it takes far longer on larger grid sizes and even worse in high-dimension spaces. The root mean squared distance a random walk travels is actually the square root of the number of time steps in one dimension. 

$$
    RMSD = \sqrt{N}
$$

In two dimensions, the walk takes even longer given there are now two axes to walk along. In three, it is even more difficult for a random walk to "stick to" the initial charge as it has to probabalistically reach the single point in an ever-expanding space.

The second criticism of the model can be remedied with tip-biasing, an approach developed to specifically model lightning's directionally-biased nature. In tip-biased DLA, the probability of the walker starting from a given point is inversely correlated with its distance from the tip of the stepped leader. It does not force the lightning in one direction, but allows it to grow in that direction with a greater probability. A normal distribution models the probability of starting from a point $n$ spaces from the tip, with the probability maximized at $n = k$. A sample distribution for k =  3 is shown below:

| Distance    | 0 |  1 |  2 | 3 |  4 |  5 | 6 |
|-------------|---|:--:|:--:|:-----:|:--:|:--:|---|
| Probability | 0 | .1 | .2 |   .4  | .2 | .1 | 0 |

This also helps remedy the scaling issue as the tip-bias dictates the random walk does not have to walk nearly as far. Thus,  the method helps to remedy the two aforementioned issues with DLA, but still does not take into account physical first-principles. 

![DLAtime](figures/DLAtime.png)
The above figure is a comparison of runtimes for tip-biased DLA and normal DLA runtimes.


![DLAtipout](figures/DLAtipout.png)
In the above image, the extreme branching pattern of tip-biased DLA can be seen, far less accurate than other methods in terms of shape, but still not as inaccurate as normal DLA.



## Dielectric Breakdown Model


![DBMout](figures/DMBout.png)

The dielectric breakdown model is a method for simulating lightning with first-principles in mind. The algorthm can be summarized in the following steps:

1. Randomly select an initial charged point on a grid.
2. Solve a discretization of the Poisson equation to determine the potential grid and determine the charge difference between the stepped leader and all points on the grid. 
3. The largest differences on the grid are the most probable to be the grids to which the stepped leader "jumps." This is considered a "step."
4. Repeat steps 2 and 3 until the lightning reaches the "ground" (bottom of the grid).

Step two is the most computationally intensive. In order to calculate the potential grid from the initial point to the ground, we must solve  the Laplacian equation, derived from Maxwell's equations for an electric field:

$$\nabla ^2 \phi = 0$$

With two-dimensional finite-differences, we have:

$$  \nabla ^2 \phi_{i,j} 
    = \left(\frac{\partial^2}{\partial x^2}+\frac{\partial^2}{\partial y^2}\right)\phi_{i,j} \\
   \nabla ^2 \phi_{i,j}  = \frac{\phi_{i,j+1}+\phi_{i+1,j}-4\phi_{i,j}+\phi_{i-1,j}+\phi_{i,j-1}}{h^2}$$
    
From the above, we get . an equation for each point on the grid, meaning we get $n\times n$ linear equationos for an $n \times n$ grid. $phi$ is a dense vector of length $n$. This can be represented as the matrix product: 

$$L_{n\times n}\cdot \phi = 0$$

This system of linear equations is where we get the $O(N^2)$ complexity we see in the computational runtimes. With a grid of 128, we get $128 \times 128$ equations and thus have a $128^2 \times 128^2$ matrix. 


We can use numerous techniques to solve this, but in the current implementation, we use the Incomplete Poisson Conjugate Gradient (IPCG) method (pseudocode below). This method is similar to the Incomplete Cholesky Conjugate Gradient (ICCG) method but uses a Poisson-specific preconditioner. 

![pseudocodeipcg](figures/ipcg.png)


The intircaes of the above approach are not critical to understand in the context of this paper. Essentxially, the above method and the Poisson preconditiona allow for only a single matrix muliplication operation is needed at a given iteration of the conjugate gradient. The preconditioner ensures convergence and thus accelerates the simulation of lightning. 

The probability of a given point being the next point the stepped leader jumps to is directly proportional to its charge:

$$ p_j = \frac{(\phi_j)^\eta}{\sum_{i \in I}(\phi_i)^\eta} $$

$\eta$ is a branching hyperparameter. For the purposes of this report, it is not relevant but it essentially controls the probability of branching in the simulation.  A greater $\eta$ value dictates a straighter stepped leader. The value used in these simulations is 4. 

However, as with DLA, this method scales poorly with problem size as the linear equation solution gets more and more complicated.

![DBMtime](figures/DBMtime.png)


# Description of your model and/or data in detail: where did it come from, how did you acquire it, what does it mean, etc.

The above methods, tip-biased DLA and DBM with IPCG were both implemented for the final project of AM205. However, these methods proved to be both incredibly memory intensive and computationally slow. Simulting (INSERT DATA HERE). Even with these improvements over the original implementations of the respective algorithms, the problem could still be solved more efficiently. When implemented, High Performance Computing was not considered and all simulations were generated on local machines. As such, selecting these models to apply HPC to was a natural decision.

However, after some initial analysis, it appeared DBM was a far better candidate for optimization than DLA. The reason for this is simple: DLA is extermely sequential. The two processes, stepped leader growth and random walks, both explicitly rely on previous steps.  The next step of the growth leader cannot be predicted without the last and the process of a random walk implicitly depends on previous steps in the random walk to calculate the next. As such, DLA was discarded.

With DBM, there is still an explicit dependence from step to step, but the process of determining the next step of the stepped leader at a given timepoint is not sequential in nature. In DLA, a random walk, the method of determining the next step, cannot be parallelized but in DBM the solving of the linear equation can be. Thus, we focused our efforts on this equation. 


#Technical description of the parallel application and programming models used

Rendering visually appealing lightning is the goal and as such we needed to generate lightning on a 1500x1500 grid, which is similar to the resolution of standard HD screens (1920×1080). Ultimately, our we sought to optimize this simulation with HPC through the parallelization of the simulation along the time domain using a multi-thread, multi-node architecture on Google Cloud Engine and Amazon Web Services. Using this approach, we obtained a non-trivial speedup and managed to simulate lightning growth on a 1500x1500 grid. 

Initial profiling of the code revealed a massive bottleneck in the dot product used in the IPCG method. This method was account for over 40% of the computation time and scaled poorly with grid size. Thus, we sought to optimize this step in particular. However, we quckly ran into a problem with this approach: the operation was already highly optimized.

During the original implementation of DBM, the choice was made to use sparse matrices to drastically increase the speed of matrix operations. This accomplished the goal of speeding up operations, but also meant our baseline code was already extremely fast. Moreover, we leveraged the numpy library further speedup the operations. Under the hood, numpy compiles in C++ and parallelizes many basic operations. Thus, for all intents and purposes, the code was already semi-parallelized. 

![percent](figures/gridpercents.png)
![matvec](figures/matdot.png)
![matmat](figures/matmat.png)

The bottleneck was not due to the operation taking a long time to complete, but rather the sheer number of calls. On a 100x100 grid, the dot product is called 90088 times, with 88200 of these being sparse-matrix-dense-vector dot products and the remaining 1888 being sparse-matrix-sparse-matrix dot products, accounting for ~50% of the total time of execution. Each sparse-matrix-dense-vector dot product took about $69 \mu s$ and $1022 \mu s $ for sparse-matrix-sparse-matrix dot products. As such,  parallelization was more difficult than expected as parallization can intorduce a massive communication overhead. This overhead can easily dominate the short function calls and negate any gains from parallelization.

In order to do this, we leveraged both thread-level parallelism with OpenMP and goroutines and node-level parallelism with MPI and gRPC. Natrually, these methods were implemented in two different implementations. One implementation utilized the techniques learned in class, OpenMP and MPI while the other used more advanced techniques with golang. 
