# Satelite-Project

To provide internet to a user, a satellite needs to form a "beam" towards that user, and the user needs to form a beam towards the satellite. If they are both 
pointing at each other, they can form a high-bandwidth wireless link.
The Starlink satellites are designed to be very flexible. For this problem, each satellite is capable of making up to 32 independent beams simultaneously. 
Therefore, one satellite can serve up to 32 users. Each beam is assigned one of 4 "colors" (which correspond to the particular frequency used to serve that 
user), which is necessary to allow a single satellite to serve users that are close to one another without causing interference.
There are a few constraints which limit how those beams can be used:
On each Starlink satellite, no two beams of the same color may be pointed within 10 degrees of each other, or they will interfere with each other.
Other non-Starlink satellites (interferers) might be trying to provide service in the same location we are. To protect them, beams from our satellites 
must not be within 20 degrees of a beam from any non-Starlink satellite (from the user's perspective).
For simplicity, we assume that every non-Starlink satellite is always providing service to all users all the time.
From the user's perspective, the beam serving them must be within 45 degrees of vertical. Assume a spherical earth, so all user normals pass 
through the center of the earth (0,0,0).

#Problem:
Given a list of users, Starlink satellites, and non-Starlink satellites, figure out how to place the beams to serve the most users, respecting the constraints 
above. It is most important to not violate any constraints, it may not be possible to cover all users in some of the provided input files.
The inputs to your program will come from a text file. Your program will receive the name of that text file on the command-line as a single argument. The input file will look like the following:
Lines that start with '#' are considered comments, and should be ignored

The input is the id and position of the Starlink satellites, users, and interferers:
sat <id> <position x y z>
user <id> <position x y z>
interferer <id> <position x y z>

Positions are in kilometers from the center of the planet.
User on the equator at the Prime Meridian, satellite 550km overhead
user 1 6371 0 0
sat 1 6921 0 0
Two users close to the North Pole, satellite 550km overhead
user 2 0 0 6371
user 3 111.189281412 0 6370.02966584
sat 2 0 0 6921
Interferer satellite in GEO at 180 degrees West (opposite the Prime Meridian)
interferer 1 -42164 0 0
Note that the provided positions use the earth-centered,earth-fixed (ECEF) coordinate system where the x-axis goes from the center of the earth through 
the point where the prime-meridian and equator intersect, the z-axis goes from the center of the earth through the north pole, and the y-axis completes the 
right hand coordinate system.
The output from your program should go to standard out, and should describe the allocation of beams between each satellite and its users.
sat 1 beam 1 user 1 color A
sat 2 beam 1 user 2 color A
sat 2 beam 2 user 3 color B
