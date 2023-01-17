## Improve search speed

Using parallel processing may improve the search speed. Try using option `-j <number of worker processes>`.

Example of searching with option `-j`:  
![](images/run9.png)

※ In this example, the option `-j6` made the time for searching reduced to approx. 1/3 of the original time.

If parallel processing does not increase CPU utilization, then your storage may be the bottleneck. If you are using HDDs, consider using SSDs.
