
 $( document ).ready(function() {
    if($("#type_text").length){
        let text1 = new TypeIt("#type_text", {
            speed: 70,
            strings: ["Hello. This is a site for easier news reading. Good read)"],
        }).go();
    }
    
    if($("#simpleUsage").length){
        let text2 = new TypeIt("#simpleUsage", {
            speed: 50,
            strings: ["Ти серйозно?», «Ми вже тут :)"],
        }).go();
    }
});
