
 $( document ).ready(function() {
    if($("#type_text").length){
        let text1 = new TypeIt("#type_text", {
            speed: 70,
            strings: ["Hello. This is a my site. Can be updated. Good read)"],
        }).go();
    }
    
    if($("#simpleUsage").length){
        let text2 = new TypeIt("#simpleUsage", {
            speed: 50,
            strings: ["Ти серйозно?», «Ми вже тут :)"],
        }).go();
    }
});
