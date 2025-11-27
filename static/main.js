import router from "./router.js"
import Header from "./components/Header.js"
import Footer from "./components/Footer.js"

var app = new Vue({
  el: '#app',
  router,
  template: `
    <div style="font-family: Arial, sans-serif;">
      <banner></banner>
      <router-view style="margin-left: 30px; margin-right: 10px;"></router-view>
      <foot></foot>
    </div>  
  `,
  data: {
    message: 'Hello Vue!'
  },
  components : { 
    "banner" : Header,
    "foot" : Footer
  }
}) 