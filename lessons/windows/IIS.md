### IIS -- Internet Information Services

[IIS](https://www.iis.net/) is the officially supported Microsoft® web server.
To learn more about it, start with [Wikepedia](https://en.wikipedia.org/wiki/Internet_Information_Services).

This lesson will brush over some possible methods of managing IIS servers using Salt. 

##### prejudice warning...

But first, an admission from the author (Vernon).

In spite of occasional flashes of brilliance (like hiring Dave Cutler and funding IronPython for two examples)
Microsoft has historically earned my profound disrespect. I look down my nose at them at every opportunity.
Nevertheless, I seem to be the guy who keeps using their stuff. 
I don't like their stuff, but the companies I work for either do, or must, and I like to have a paycheck,
so I keep using it.  I remember a Salt Lake Python User's Group meeting one night after which the attendees started
talking about creating a replacement for Chef and Puppet written in Python. I took an informal survey of the
laptops in the room. They were mostly Ubuntu or local Utah companies Linux, along with several Macs. 
There was exactly one computer running Windows. In my meek defense, mine would also dual-boot Ubuntu, 
but that night I was working on a Windows project, so guess what I was running.

Later, at [eHealth Africa](https://www.ehealthafrica.org/) 
\[thank you, Bill and Melinda Gates, for the generous donations which paid for much more than my salary\] 
we ran Linux servers -- except for the one monster [SQL Server](https://www.microsoft.com/en-us/sql-server/sql-server-2017) 
database which kept our [ArcGIS](https://www.arcgis.com) application happy. 
I had to write a system to copy some of our PostgreSQL data into it.
(And an upgrade to [adodbapi](https://sourceforge.net/projects/adodbapi/) to accomplish that.)

Now, at [Sling TV](https://www.sling.com) we have several data centers bulging with Linux servers.
Hidden amoung them are the servers for Microsoft's [PlayReady](https://www.microsoft.com/playready/) content
protection product. (It is one of three similar systems which we use.) 
We recently doubled our number of PlayReady servers -- from two up to four. 
That experience caused a request to land on my desk: make Salt state scripts to deploy PlayReady.  
Oh, and also to deploy a PlayReady build server. 
So I sweep the [spiderwebs](https://goo.gl/images/ujmLNk) out of my Windows machine and here we go again.

So, for those who are forced to support these poorly performing platforms that yet cost so much money,
read on. This is not going to be a lesson as much as a blog about my learning experience.

#### Salt vs PowerShell vs GUI

Microsoft makes wonderful GUI configuration tools for its software. 
They are great for people who use them every day, or even every month.
Click here, click there, and you have got it. Wonderful.

But not so wonderful if you need to keep several machines configured exactly the same.

So, after doing a lot of research, you can write PowerShell scripts to do the configuration.
Which is fine until you need to change a key parameter.  
Then good luck remembering (or learning) where it is.

And good luck figuring out (or documenting) what must be clicked on a GUI before your run the script.

Here we will discuss some Salt scripts to do the installation and management in a reliable and repeatable way.
Key parameters will be maintained in Pillar files.

