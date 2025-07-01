<template>
  <nav class="navbar navbar-expand-lg bg-dark">
    <div class="container-fluid">
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNavAltMarkup">
        <div class="navbar-nav ms-auto"> <!-- ms-auto 用于右对齐 -->
          <router-link class="nav-link" to="/Home">Home</router-link>
          <router-link class="nav-link" to="/project-intro">Introduction</router-link>
          <router-link class="nav-link" to="/product-market">Production</router-link>
          <router-link class="nav-link" to="/about">About</router-link>
          <router-link class="nav-link" to="/page-wrapper"></router-link>
        </div>
      </div>
    </div>
  </nav>
  <router-view></router-view>
</template>

<style>
nav {
  background-color: #000000; /* 黑色背景 */
}

nav .nav-link {
  color: white; 
  font-weight: bold;
  margin-right: 30px;
}

nav .nav-link.router-link-exact-active {
  background: linear-gradient(to right, #e66465, #9198e5); /* 设置渐变背景 */
  -webkit-background-clip: text; /* Chrome 和 Safari */
  background-clip: text;
  color: transparent;
}
</style>
