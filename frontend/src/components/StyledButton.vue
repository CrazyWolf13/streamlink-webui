<template>
    <div class="styled_button_container" :style="gradientStyle">
      <button @click="onClick"><slot /></button>
    </div>
  </template>
  
  <script>
  export default {
    name: "StyledButton",
    props: {
      gradient: {
        type: String,
        default: "linear-gradient(90deg, #6441a5, #322052)",
      },
      clickHandler: {
        type: Function,
        default: () => {},
      },
    },
    computed: {
      gradientStyle() {
        return {
          background: this.gradient,
        };
      },
    },
    methods: {
      onClick() {
        this.clickHandler();
      },
    },
  };
  </script>
  
  <style scoped>
button {
  font-size: 1.4em;
  padding: 0.6em 0.8em;
  border-radius: 0.5em;
  border: none;
  background-color: #18181a;
  color: #fff;
  cursor: pointer;
  box-shadow: 2px 2px 3px #000000b4;
  width: 100%;
  margin: 1px 1px 1px 1px;
  box-sizing: border-box;
}

.styled_button_container {
  position: relative;
  padding: 3px;
  background: linear-gradient(90deg, #6441a5, #322052);
  border-radius: 0.9em;
  transition: all 0.4s ease;
  margin: 50px 50px 50px 50px;
  display: flex;
  justify-content: center;
}

.styled_button_container::before {
  content: "";
  position: absolute;
  inset: 0;
  margin: auto;
  border-radius: 0.9em;
  z-index: -10;
  filter: blur(0);
  transition: filter 0.4s ease;
}

.styled_button_container:hover::before {
  background: linear-gradient(90deg, #6441a5, #322052);
  filter: blur(1.2em);
}
.styled_button_container:active::before {
  filter: blur(0.2em);
}

  </style>