<template>
  <div class="styled_button_container" :class="containerClasses">
    <button @click="onClick"><slot /></button>
  </div>
</template>

<script>
export default {
  name: "StyledButton",
  props: {
    variant: {
      type: String,
      default: "primary",
    },
    clickHandler: {
      type: Function,
      default: () => {},
    },
  },
  computed: {
    containerClasses() {
      return [`gradient-${this.variant}`];
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
  font-size: 1.1rem;
  padding: 0.6em 0.9em;
  border-radius: 0.5em;
  border: none;
  background-color: #18181a;
  color: #fff;
  cursor: pointer;
  box-shadow: 2px 2px 3px #000000b4;
  width: 100%;
  margin: 0;
  box-sizing: border-box;
}

.styled_button_container {
  position: relative;
  padding: 3px;
  border-radius: 0.9em;
  transition: all 0.3s ease;
  margin: 12px 0;
  display: flex;
  justify-content: center;
}

/* Gradient variants */
.gradient-primary {
  background: linear-gradient(90deg, #6441a5, #322052);
}

/* Glow on hover */
.styled_button_container::before {
  content: "";
  position: absolute;
  inset: 0;
  margin: auto;
  border-radius: 0.9em;
  z-index: -10;
  filter: blur(0);
  transition: filter 0.3s ease;
}

.styled_button_container:hover::before {
  background: inherit;
  filter: blur(1em);
}

.styled_button_container:active::before {
  filter: blur(0.2em);
}

/* Compact modifier for smaller inline buttons */
.small-button {
  max-width: 200px;
  margin: 0;
}
</style>
