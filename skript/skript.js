
 $( document ).ready(function() {
    if($("#type_text").length){
        let text1 = new TypeIt("#type_text", {
            speed: 70,
            strings: ["Привiт, вiтаю вас тут. Це мiй сайт-вiзитка. Вiн поки що на стадii розробки :)"],
        }).go();
    }
    
    if($("#simpleUsage").length){
        let text2 = new TypeIt("#simpleUsage", {
            speed: 50,
            strings: ["Ви серйозно?», «Ви вже на GitHub :)"],
        }).go();
    }
});
