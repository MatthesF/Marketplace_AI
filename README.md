
<table>
  <tr>
    <td>
      <p>
      <h1> Marketplace AI </h1>
      If user wants to sell, user must provide:</p>
      <ul>
        <li><code>products_images</code></li>
      </ul>
      I do the rest -- money come soon!"
    </td>
    <td>
      <img src="assets/image.png" alt="drawing" width="300px"/>
    </td>
  </tr>
</table>
       


## Flow 

<img src="assets/flow_v0.png" alt="Flow"/>

## Next up

- [x] Clean up `README`, to redefine the target
- [ ] Draw LangGraph graph
- [ ] Include user info input
- [ ] Clean up structure
  - [ ] All backend functionality should move to `src`
  - [ ] Merge implementations
- [ ] Increase robustness
  - [ ] Use path library
  - [ ] Implement testing
- [ ] Additional features
  - [ ] Implement reflection loop
  - [ ] Improve price estimation
  - [ ] Prompt user for more info or new images
  - [ ] Switch to `flask`?
  - [ ] Implement auto clicker with vision
  - [ ] Make chain for separating images by product when given many

## Research Questions

- Should we provide all pictures at once or one by one?
- Should we fine-tune the model? What could be gained?
- For price estimation, should we:
    1. Use a database for lookups?
    2. Perform online searches?
    3. Use the base model for predictions?
- Should the price estimator be region-aware? Is urgency relevant?
- Should we use a multi-agent or single-agent approach?
- How can we effectively perform A/B testing for different prompts?



## Sources
**For preperation**
- **Udemy Course**: [LangChain: Building Chatbots and AI Assistants](https://www.udemy.com/course/langchain/learn/lecture/43404740#overview)
- **YouTube Course**: [AI & Machine Learning Playlist](https://www.youtube.com/playlist?list=PLfaIDFEXuae2LXbO1_PKyVJiQ23ZztA0x)
- **Udemy Course**: [LangGraph](https://www.udemy.com/course/langgraph/learn/lecture/43455286#overview)