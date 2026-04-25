<template>
  <div class="star-spinner" style="width: 24px; height: 24px">
    <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <g class="star-group star-center">
        <path
          d="M12 2L14.09 8.26L20 9.27L15 13.14L16.18 19.02L12 15.77L7.82 19.02L9 13.14L4 9.27L9.91 8.26L12 2Z"
          fill="#b1adf3"
          class="star-path"
        />
      </g>
      <g class="star-group star-1" transform="translate(12, 12)">
        <path
          d="M12 2L14.09 8.26L20 9.27L15 13.14L16.18 19.02L12 15.77L7.82 19.02L9 13.14L4 9.27L9.91 8.26L12 2Z"
          fill="#b1adf3"
          class="star-path"
          transform="scale(0.5) translate(0, -16)"
        />
      </g>
      <g class="star-group star-2" transform="translate(12, 12)">
        <path
          d="M12 2L14.09 8.26L20 9.27L15 13.14L16.18 19.02L12 15.77L7.82 19.02L9 13.14L4 9.27L9.91 8.26L12 2Z"
          fill="#b1adf3"
          class="star-path"
          transform="scale(0.5) translate(16, 0)"
        />
      </g>
      <g class="star-group star-3" transform="translate(12, 12)">
        <path
          d="M12 2L14.09 8.26L20 9.27L15 13.14L16.18 19.02L12 15.77L7.82 19.02L9 13.14L4 9.27L9.91 8.26L12 2Z"
          fill="#b1adf3"
          class="star-path"
          transform="scale(0.5) translate(0, 16)"
        />
      </g>
      <g class="star-group star-4" transform="translate(12, 12)">
        <path
          d="M12 2L14.09 8.26L20 9.27L15 13.14L16.18 19.02L12 15.77L7.82 19.02L9 13.14L4 9.27L9.91 8.26L12 2Z"
          fill="#b1adf3"
          class="star-path"
          transform="scale(0.5) translate(-16, 0)"
        />
      </g>
    </svg>
  </div>
</template>

<script setup></script>

<style scoped>
.star-spinner {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: relative;

  svg {
    transform-origin: 12px 12px;
  }

  .star-center {
    transform-origin: 12px 12px;
    animation: starTwinkle 1.5s ease-in-out infinite;
  }

  .star-1,
  .star-2,
  .star-3,
  .star-4 {
    transform-origin: 0 0;
    animation:
      starOrbit 3s linear infinite,
      starTwinkle 1.5s ease-in-out infinite;
  }

  .star-1 {
    animation-delay: 0s, 0s;
  }
  .star-2 {
    animation-delay: 0s, 0.3s;
  }
  .star-3 {
    animation-delay: 0s, 0.6s;
  }
  .star-4 {
    animation-delay: 0s, 0.9s;
  }

  .star-path {
    transform-origin: center;
    fill: #818cf8; /* 这里使用了你项目中的主色调，你可以根据自己的项目调整 */
  }
}

@keyframes starOrbit {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes starTwinkle {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}
</style>
