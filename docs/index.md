# Abstract

Fractal growth is a comutationally intensive simulation which has typically ignored traditionoal first principles in physics in order to increase speed. Lightning is a well understood phenomena that can be simulated accurately with the Dielectric Breakdown Model, but it is computationally expensive to do so. We seek to optimize this simulation with HPC through the parallelization of the simualtion at each time step using a multi-node architecture on Google Cloud Engine. Using this approach, we obtained a non-trivial speedup and amanged to simulate lightning growth on a 1500x1500 grid.


# Problem Statement
One of the biggest promises of HPC is allowing for realistic modelling of the physical world. This pursuit is nontrivial as physical descriptors of nature often require high-dimensional space, big data, and intensive computations that do not scale well as spatial or temporal resolution are increased. Models often trade off performance for accuracy as they grow in complexity. One such domain is the use of computing to simulate lightning dispersion as is nucleates from a point in the air towards the ground. These models either rely on naive toy models that essentially propagate a point towards the ground randomly or physical models that rely on electrodynamics and fractal growth to efficiently simulate lightning dispersion. The aim is to implement the physical model through first principles while offseting some of the computing and scaling bottlenecks through HPC principles. 

Fractal growth is a computationally intensive simulation which has typically ignored traditionally first principles in physics in order to increase speed despite the fact that these growth patterns can be found in a wide-range of of phenomenon from biology to physics and chemistry. Lightning is a well understood phenomena that can be simulated accurately with the Dielectric Breakdown Model, but it is computationally expensive to do so. This model relies on solving discritized differential equations on enormous grids with unfavorable scaling. This has bottlenecked any sort of physical implementation. 

In order to accurately simulate lightning based on first-principles, the Dielectric Breakdown Model is used. In this method, the charge distribution over a given grid is calculated by solving the Poisson equation. However, solving this partial differential equation is compuataionally expensive, requiring an expansion of the grid used. In order to solve for the growth at each time step on a 100 x 100 grid, one must solve for the dot product of a 10,000x10,000 matrix and a 10,000 element vector (or another square matrix). Obviously, this $O(N^2)$ scaling is inefficient but luckily matrix operations are easily parallelizable in theory. 



# Previous Work

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

![DBMout](figures/DBM.png)

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


# Model Origins

The above methods, tip-biased DLA and DBM with IPCG were both implemented for the final project of AM205. However, these methods proved to be both incredibly memory intensive and computationally slow. Simulting (INSERT DATA HERE). Even with these improvements over the original implementations of the respective algorithms, the problem could still be solved more efficiently. When implemented, High Performance Computing was not considered and all simulations were generated on local machines. As such, selecting these models to apply HPC to was a natural decision.

However, after some initial analysis, it appeared DBM was a far better candidate for optimization than DLA. The reason for this is simple: DLA is extermely sequential. The two processes, stepped leader growth and random walks, both explicitly rely on previous steps.  The next step of the growth leader cannot be predicted without the last and the process of a random walk implicitly depends on previous steps in the random walk to calculate the next. As such, DLA was discarded.

With DBM, there is still an explicit dependence from step to step, but the process of determining the next step of the stepped leader at a given timepoint is not sequential in nature. In DLA, a random walk, the method of determining the next step, cannot be parallelized but in DBM the solving of the linear equation can be. Thus, we focused our efforts on this equation. 


#Goal

Rendering visually appealing lightning is the goal and as such we needed to generate lightning on a 1500x1500 grid, which is similar to the resolution of standard HD screens (1920×1080). Ultimately, our we sought to optimize this simulation with HPC through the parallelization of the simulation along the time domain using a multi-thread, multi-node architecture on Google Cloud Engine and Amazon Web Services. Using this approach, we obtained a non-trivial speedup and managed to simulate lightning growth on a 1500x1500 grid. 

# Profiling

Initial profiling of the code revealed a massive bottleneck in the dot product used in the IPCG method. This method was account for over 40% of the computation time and scaled poorly with grid size. Thus, we sought to optimize this step in particular. However, we quckly ran into a problem with this approach: the operation was already highly optimized.

During the original implementation of DBM, the choice was made to use sparse matrices to drastically increase the speed of matrix operations. This accomplished the goal of speeding up operations, but also meant our baseline code was already extremely fast. Moreover, we leveraged the numpy library further speedup the operations. Under the hood, numpy compiles in C++ and parallelizes many basic operations. Thus, for all intents and purposes, the code was already semi-parallelized. 

![percent](figures/gridpercents.png)
![matvec](figures/matdot.png)
![matmat](figures/matmat.png)

The bottleneck was not due to the operation taking a long time to complete, but rather the sheer number of calls. On a 100x100 grid, the dot product is called 90088 times, with 88200 of these being sparse-matrix-dense-vector dot products and the remaining 1888 being sparse-matrix-sparse-matrix dot products, accounting for ~50% of the total time of execution. Each sparse-matrix-dense-vector dot product took about $69 \mu s$ and $1022 \mu s $ for sparse-matrix-sparse-matrix dot products. As such,  parallelization was more difficult than expected as parallization can intorduce a massive communication overhead. This overhead can easily dominate the short function calls and negate any gains from parallelization.

# Initial Attempts
In order to do this, we leveraged both thread-level parallelism with OpenMP and goroutines and node-level parallelism with MPI and gRPC. Natrually, these methods were implemented in two different implementations. One implementation utilized the techniques learned in class, OpenMP and MPI while the other used more advanced techniques with golang. Moreover, we attempted to accelerate the dot prodcut of sparse matrices using PyCuda. Of these three initial implementations, only two were successful, albeit in altered forms. PyCuda was eliminated based on heavy data copying costs, while MPI and gRPC suffered from similar overheads due to cluster latency (see roadblocks). 

# Discoveries

As we continued to implement our planned architecture, some key discoveries allowed us to further enhance the performance of the model. 

## Shared Libraries vs Subprocess

Given the model was implemented in python already and a complete rewrite in C++ would be incredibly difficult with the number of library dependencies, a method of calling functions in other languages was needed. We were then faced with a decision between calling . functions from a shared library (ctypes) and spawning a python subprocess. The table below compares the time to spawn a subprocess or call a shared library with the time to complete one dot product on a 1500 x 1500 grid:

|                | Time Spawn ($\mu s$ )| % Matrix-Matrix Dot  | % Matrix-Vector Dot |
|----------------|--------------------|-------------------------|-------------------------|
| Subprocess     | 4701               | 2                      | 52                       |
| Shared Library | 845                | .4                    | .9                 |

Beyond simply being approximately 5x faster than a subprocess, a shared library is significantly faster on subsequent calls than the initial call:

|        | Time Spawn ($\mu s$) |
|--------|--------------------|
| First Call  | 1270               |
| Second Call | 72                 |

## Sparse Matrices

We quickly discovered that the matrices we were working with were extremely sparse:


|        | % Non-zero Elements |
|--------|---------------------|
| Matrix | .04                 |
| Vector | 95                  |

This meant that even though we had large matrices, we could encode them into much smaller arrays. Sparse matrices work by encoding the data and indices of non-zero elements in the matrices in an easy-to-access 3 array system. While the in-depth implementation is irrelevant for the purposes of this experiment,  the use of sparse matrices significantly accelerates matrix operations by ignoring multiplcation of zero elements.

More relevant to our implementation, however, was the fact that any implementation had to leverage this previous speedup rather than revert back to dense matrices. 

## Vector Addition

In further profiling, it was discovered that vector addition operations account for a signifcant portion of the runtime of the function pcg in the code. Three lines, addition assignment,  subtraction assignment and addition, all followed by multiplication (i.e. a += b * c) accounted for 65.5% of the runtime of pcg on a 1500x1500 grid. 

Quickly parallelizing these processes (thread-level with goroutines) yielded a 66% speedup, reducing the runtime of these three lines to only 19% of pcg.

This was a massive speedup for a trivial solution. This prompted us to search the code for other quickly parallelizable lines that would yield a boost to performance beyond the dot product. 

## Empty vs Zero

One such line was the use of numpy zeros instead of numpy empty. Numpy zeros obviously allocates zeros in a given shape while numpy empty simply sets the object's shape without populating elements.

The Go implementation continues when a row is empty, not when a row is 0. Thus, by initializing elements as empty instead of 0, the code iterates much faster,  moving on to the rows that actually matter sooner. This yielded a 30% speedup on our local machine with a 1500x1500 grid:

|       | Time ($\mu s$) |
|-------|----------------|
| Zeros | 13260          |
| Empty | 9285           |

# Roadblocks



While we attempted to implement the proposed architecture without changes, some changes were necessary given the constraints of the technologies we were using.

## Multiprocressing
One of the first problems we faced in the entire project was realizing that the easy implementation of the code we had in python would need to be converted to to C in order to properly speed up and make use of the design principles from the course. The implementation of a simply python multiprocessing version of the script made this clear as most of the python code used wrapper functions for latent C code or was interdependent and thus made a parallelized version of the code impossible without a lower-level implementation. 

## PyCuda

As mentioned before, the runtime of a dot product is fairly short (<10000$ \mu s$ ono 1500 x 1500 grid). Thus, any attempt to parallelize will have to ensure that the communication overhead is not too significant. Communication overheads are greater in shared memory architetures than non-shared memory architectures. Thus, multi-threading introduces less overhead than multi-processing. 

When PyCuda is invoked, it must copy over the data to the GPU before the operation can be executed. This means a significant overhead is introduced. In order to test this, the transfer times of various grid sizes were tested on an AWS g3 instance (see appendix for specifications). These results are tabulated below for a .04% non-zero elements matrix:

| Grid Size (n x n) | Time ($\mu s$) | % of Matrix-Vector Dot |
|-------------------|----------------|------------------------|
| 64                | 265238         | 2,947                  |
| 150               | 1576900        | 17,521                 |
| 300               | 19009656       | 211,218                |


![transfer](figures/transfer.png)


As can be seen above, the transfer time far outweighs the time of an operation, resulting in a slowdown for the operation.Thus, PyCuda was abandoned as a possible implementation.


## Latency

Similar to above, multi-node architectures had to be abandoned due to latency resulting in too great of an overhead. Using a cluster of 8 c5 worker instances and one t2 master instance (see appendix), gRPC was tested but quickly abandoned. With a latency of about 3000 $\mu s$ on a 1080x1080 grid, the latency was significant. Further testing revealed that the average matrix-vector dot product on a 1500x1500 grid was 2184293 $\mu s$:

|      | Time ($\mu s$) | % of Matrix-Vector Dot |
|------|----------------|------------------------|
| gRPC | 2184293        | 24,269                 |

## Memory Error

After approximately 13 hours of real time and approxiamtely 375 hours of compute time on a GCE instance (see appendix), the run failed to generate a 1400x1400 simulation because of memory issues. In order to generate the movie, the array of grids is copied for rendering. This means the (INSERT SIZE) array essentially doubles, resulting in far more memory being used than we expected. As such, we requested an increased memory of 600GB total. In order to prevent the need to rerun in the event of a failed render, we also write the array to disk before rendering. This meant we had to request a total of (INSERT SIZE) in disk size as well.

# OpenMP + MPI

An MPI hybrid implementation was 
  



## Results

#OpenMP + MPI

# Golang (gourouteines + gRPC)

## Results

# Appendix
