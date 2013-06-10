#!/usr/bin/python

import mmap
import re
import os
import sys
import json
import tempfile
import pickle
from datetime import datetime 
from itertools import groupby
import matplotlib.pyplot as plt
import numpy as np

class Build:
    pass
    
class Project:
    pass    

class ProjectStatistics:
    def __init__(self, name, projectIterator):
        self.name= name
        
        compilationsList = list(projectIterator)
        noTrivialCompilationsList = [project for project in compilationsList if project.Time>1000]
        
        times = [prj.Time for prj in compilationsList]
        noTrivialTimes = [prj.Time for prj in noTrivialCompilationsList]
        
        self.numCompilations = len(compilationsList)
        self.noTrivialNumCompilations = len(noTrivialCompilationsList)
        self.timeSum = sum(times)
        self.noTrivialTimeSum = sum(noTrivialTimes)
        self.meanTime = (self.timeSum/self.numCompilations) if self.numCompilations>0 else 0
        self.noTrivialMeanTime = (self.noTrivialTimeSum/self.noTrivialNumCompilations) if self.noTrivialNumCompilations>0 else 0
        self.maxTime = max(times) if len(times)>0 else 0

        
        
def replace_javascriptdatatime (filename):
    f=open(filename)
    size = os.stat(filename).st_size
    data = mmap.mmap(f.fileno(), size, access=mmap.ACCESS_READ)
    m = re.compile(r'\:new Date\(([0-9]*)\)')
    result = m.sub(r':"\1"',data)
    return result

def top_of_list (iterable, numItems):
    i=0
    for item in iterable:
        yield item
        i+=1
        if i == numItems:
            return
        
def print_stats(sortedStats, propery):
    for stat in top_of_list(sortedStats,10):
        print '{1:15} {0} '.format(stat.name, getattr(stat, propery))
        



def createPicked (fileName, fileExtension):

    replaced =replace_javascriptdatatime(filename)

    print('Data times replaced')
    tmpFile =tempfile.NamedTemporaryFile(mode='w+')
    tmpFile.write(replaced)
    tmpFile.flush()
    print(tmpFile.name  + ' wrote')
    tmpFile.seek(0)
    parsed = json.load(tmpFile)
    print('JSON reloaded')

    builds=[]
    projects=[]
    for build in parsed:
        
        s = Build()
        s.Start= build['Start']
        s.Name = build['Solution']['Name']
        s.Time = build['Time']
        s.DateTime = datetime.fromtimestamp( int(build['Start'])/1000)
        
            
        builds.append(s)
        
        for project in build['Projects']:
            p = Project()
            p.SolutionName = s.Name
            p.Name = project['Project']['Name']
            p.Time = project['Time']
            projects.append(p)

    output = open(fileName + '.pkl', 'wb')
    pickle.dump((projects, builds), output, -1)
    output.close()
    print 'Done'
    
def dayName(day):
    # day is a iso day number, 1 for monday, 7 for sunday
    translations= ['Mon.','Tue.','Wed.','Thu.','Fri.','Sat.','Sun.']
    return translations[day-1]
    

def milisecondsToHours(miliseconds):
    return miliseconds/1000.0/60/60

def milisecondsToMins(miliseconds):
    return miliseconds/1000.0/60
    
def showBuildsGraph(groupedBuilds):
    days = []
    times = []
    for day, time in groupedBuilds:
        days.append(dayName(day))
        times.append(milisecondsToHours(time))
        
    N = len(days)
    
    ind = np.arange(N)  # the x locations for the groups
    width = 1     # the width of the bars

    rects1 = plt.bar(ind, times, width, color='r')

    # add bars
    plt.ylabel('Hours')
    plt.title('Time by day')
    plt.xticks(ind+(width/2.0), days )
    # plt.legend( rects1[0], 'Time (min.)' )

    
    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            plt.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%.2f'%float(height),
                    ha='center', va='bottom')
                    
    autolabel(rects1)

    plt.show()

        
def loadShowPicked (fileName, fileExtension):
    print 'Loading data'
    
    pkl_file = open(fileName+fileExtension, 'rb')

    projects, builds = pickle.load(pkl_file)
    pkl_file.close()
   
    
    print '\nSolution statistics'
    buildDates  = map(lambda build:build.DateTime, builds)
    minDateTime= min(buildDates)
    maxDateTime= max(buildDates)
    
    
    print 'Initial day: ' + str(minDateTime)
    print 'End day: ' + str(maxDateTime) 
    labourDays = ((maxDateTime-minDateTime).days/7.0 *5)
    buildTimes  = map(lambda build:build.Time, builds)
    totalMiliseconds = sum(buildTimes)
    print 'Total Time (hours): {0:.2f}'.format(milisecondsToHours(totalMiliseconds) )
    print 'Labour days: {0:.2f}'.format(labourDays)
    print 'Mean time Time (labour days) (mins): {0:.2f}'.format(milisecondsToMins(totalMiliseconds)/labourDays)
    
    
    # order and group builds data by day of week (1- mon, 7- sun)
    sortedBuilds= sorted(builds, key=lambda build: build.DateTime.isoweekday())
    groupedBuilds=[]
    for day, dayBuilds in groupby(sortedBuilds, lambda build: build.DateTime.isoweekday()):
        groupedBuilds.append((day, sum(map(lambda g: g.Time,list(dayBuilds)))))
    
    for key, time in groupedBuilds:
        print 'Day: {0} Hours {1:.2f} '.format(dayName(key), milisecondsToHours(time))
        
    showBuildsGraph(groupedBuilds)
    
    
    print 'Projects statistics'

    projects = sorted(projects, key=lambda project: project.Name)
    groupedProjects=[]
    for key, group in groupby(projects, lambda x: x.Name):
        groupedProjects.append((key, list(group)))

    projectStats = [ProjectStatistics(group[0],group[1]) for group in groupedProjects]

    print 'Creating builds statistics'
    
    print '\nTop 10 most compiled projects'
    sortedStats= sorted(projectStats, key=lambda stats: stats.numCompilations, reverse=True)
    print_stats(sortedStats,'numCompilations')

    print '\nTop 10 total time consuming projects'
    sortedStats= sorted(projectStats, key=lambda stats: stats.timeSum, reverse=True)
    print_stats(sortedStats,'timeSum')

    print '\nTop 10 mean time consuming projects'
    sortedStats= sorted(projectStats, key=lambda stats: stats.meanTime, reverse=True)
    print_stats(sortedStats,'meanTime')

    print '\nTop 10 most no-trivial compiled projects'
    sortedStats= sorted(projectStats, key=lambda stats: stats.noTrivialNumCompilations, reverse=True)
    print_stats(sortedStats,'noTrivialNumCompilations')

    print '\nTop 10 total no-trivial time consuming projects'
    sortedStats= sorted(projectStats, key=lambda stats: stats.noTrivialTimeSum, reverse=True)
    print_stats(sortedStats,'noTrivialTimeSum')

    print '\nTop 10 mean no-trivial time consuming projects'
    sortedStats= sorted(projectStats, key=lambda stats: stats.noTrivialMeanTime, reverse=True)
    print_stats(sortedStats,'noTrivialMeanTime')

    print '\nTop max time consuming projects'
    sortedStats= sorted(projectStats, key=lambda stats: stats.maxTime, reverse=True)
    print_stats(sortedStats,'maxTime')

   
filename=sys.argv[1]    
fileName, fileExtension = os.path.splitext(sys.argv[1])

if (fileExtension=='.json'):
    createPicked (fileName, fileExtension)
else:
    loadShowPicked (fileName, fileExtension)


