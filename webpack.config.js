const path = require('path');

module.exports = {
  entry: './app/static/js/main.js',
  output: {
    path: path.resolve(__dirname, 'app/static/dist'),
    filename: 'bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      }
    ]
  },
  devServer: {
    static: {
      directory: path.join(__dirname, 'app/static/dist'),
    },
    compress: true,
    hot: true,
  }
};
