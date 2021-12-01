import pandas as pd
if __name__ == "__main__":
    data = pd.read_csv("vendor_clusters.csv",sep=',',index_col=0)
    count={}
    for i in range(len(data)):
        if data["vendor"][i] not in count:
            count[data["vendor"][i]]=[0]*3
        count[data["vendor"][i]][data["cluster"][i]]+=1
    c0, c1, c2 = {}, {}, {}
    s0, s1, s2 = 0,0,0
    for key in count.keys():
            s0+=count[key][0]
            s1+=count[key][1]
            s2+=count[key][2]
            
    for key in count.keys():
            c0[key]=count[key][0]/s0
            c1[key]=count[key][1]/s1
            c2[key]=count[key][2]/s2