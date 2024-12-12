let result=document.getElementById("xkresult").getElementsByTagName('tbody')[0].childNodes;
list=[];
for(var i=0; i<result.length; i++){
    detail={};
    detail["subject"]=result[i].childNodes[0].innerText;
    detail["result"]=result[i].getElementsByTagName("span")[0].className.indexOf("danger")==-1
    detail["detail"]=result[i].getElementsByTagName("span")[0].innerText;
    list.push(detail);
}
//console.log(JSON.stringify (list));
return JSON.stringify (list); 