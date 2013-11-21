/**
* RobinTang
* 2013-11-21
*/

// 公共的js代码
// 主要用于全局样式控制


function loginfo(){
	console.log("有兴趣一起来做这个公众账号?");
    console.log("e-mail: trbbadboy@qq.com");
    console.log("QQ: 472497084");
}

loginfo();

if(typeof($) != "undefined"){
    $(function(){
        $(".copyright").append("©2013 Sin, sintrb@gmail.com");
    });
}
