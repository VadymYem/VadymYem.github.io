
 $( document ).ready(function() {
    if($("#type_text").length){
        let text1 = new TypeIt("#type_text", {
            speed: 70,
            strings: ["Привіт, вітаю вас тут. Це мій сайт-візитка. Він поки що на стадії розробки :)"],
        }).go();
    }
    
    if($("#simpleUsage").length){
        let text2 = new TypeIt("#simpleUsage", {
            speed: 50,
            strings: ["Ви серйозно?», «Ви вже на GitHub :)"],
        }).go();
    }
});