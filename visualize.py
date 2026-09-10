import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.lines as mlines

def viscwn(logfile):
  f = open(logfile)
  flows = {}
  for line in f:
    line = line.strip()
    if line.find("FLOW")==0:
      blah,time,name,cwnd,data,rtt,rate,state = line.split(',')
      if name not in flows:
        flows[name] = [[],[],[],[],[],[]]
      flows[name][0].append(float(time))
      flows[name][1].append(float(cwnd))
      flows[name][2].append(int(data))
      flows[name][3].append(float(rtt))
      flows[name][4].append(float(rate))
      flows[name][5].append(state)
  f.close()
  return flows

def visbuf(logfile):
  f = open(logfile)
  links = {}
  for line in f:
    line = line.strip()
    if line.find("BUF")==0:
      blah,time,name,bufsz,buflen,blah = line.split(',')
      if name not in links:
        links[name] = [[],[],[]]
      links[name][0].append(float(time))
      links[name][1].append(int(bufsz))
      links[name][2].append(int(buflen))
  f.close()
  return links

def plotlink(links, nm, j, ylabel='Buffer data (bytes)'):
  i=0
  if isinstance(nm,list):
    for n in nm:
      if n in links:
        plt.plot(links[n][i],links[n][j],label=n)
      plt.legend()
  else:
    plt.plot(links[nm][i],links[nm][j])
  plt.xlabel('time (s)')
  plt.ylabel(ylabel)

def plotflow(flows, nm, j, ylabel='Congestion Window Size', state=False):
  i=0

  if state and not isinstance(nm,list):
    r = (1,0,0)
    g = (0,1,0)
    b = (0,0,1)
    clrs = np.zeros((flows[nm][3].shape[0],3))
    clrs[flows[nm][-1]=='SS']=g
    clrs[flows[nm][-1]=='CA']=b
    clrs[flows[nm][-1]=='FR']=r
    points = np.array([flows[nm][i], flows[nm][j]]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    lc = LineCollection(segments, colors=clrs)
    lc.set_linewidth(1.7)
    fig, ax = plt.subplots()
    ax.add_collection(lc)
    ax.autoscale_view()

    line_ss = mlines.Line2D([], [], color='green', label='Slow Start')
    line_ca = mlines.Line2D([], [], color='blue', label='Congestion Avoidance')
    line_fr = mlines.Line2D([], [], color='red', label='Fast Recovery')
    plt.legend(handles=[line_ss,line_ca,line_fr])
  else:
    if isinstance(nm,list):
      for n in nm:
        if n in flows:
          plt.plot(flows[n][i],flows[n][j],label=n)
    else:
      plt.plot(flows[nm][i],flows[nm][j])
    plt.legend()
  plt.xlabel('time (s)')
  plt.ylabel(ylabel)
  return plt.gca()

def main(logfile, flow_names=None, link_names=None, output_prefix=None):
  """Plot congestion-window and link-buffer measurements from a simulator log."""
  links = visbuf(logfile)
  for link in links:
    links[link] = np.array(links[link])

  flows = viscwn(logfile)
  for flow in flows:
    # Keep the state column as strings while retaining numeric plot data.
    flows[flow] = [np.asarray(column) for column in flows[flow]]

  flow_names = flow_names or sorted(flows)
  link_names = link_names or sorted(links)

  # Flow column 1 is congestion window size.
  plotflow(flows, flow_names, 1)
  plt.tight_layout()
  if output_prefix:
    plt.savefig(output_prefix + '_cwnd.png', dpi=150)
  # Link column 1 is buffer data in bytes.
  plt.figure()
  plotlink(links, link_names, 1)
  plt.tight_layout()
  if output_prefix:
    plt.savefig(output_prefix + '_buffers.png', dpi=150)
  else:
    plt.show()


if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser(description='Plot measurements from a simulator log')
  parser.add_argument('logfile')
  parser.add_argument('--flows', nargs='+', help='flow names to plot (default: all)')
  parser.add_argument('--links', nargs='+', help='link names to plot (default: all)')
  parser.add_argument('--output-prefix', help='save <prefix>_cwnd.png and <prefix>_buffers.png')
  args = parser.parse_args()
  main(args.logfile, args.flows, args.links, args.output_prefix)
