# AI-Powered Recommendations

## Overview

SpendSense MVP V2 now supports AI-powered recommendation generation using OpenAI's API. This feature allows operators to generate personalized financial recommendations using advanced language models alongside the existing rule-based system.

## Features

- **AI-Generated Recommendations**: Generate personalized recommendations using OpenAI's GPT models
- **Model Selection**: Choose from multiple OpenAI models (gpt-4o-mini, gpt-4o, gpt-3.5-turbo)
- **Customizable Output**: Control the number of recommendations generated (1-10)
- **Guardrails**: AI recommendations are subject to the same tone validation and compliance checks as rule-based recommendations
- **Transparency**: Token usage is displayed for cost tracking
- **Fallback**: Automatically falls back to rule-based recommendations if AI generation fails

## How to Use

### 1. Access the Operator Dashboard

Launch the NiceGUI operator dashboard:

```bash
uv run python ui/app_operator_nicegui.py
```

The dashboard will open in your browser at http://localhost:8081

### 2. Navigate to Recommendation Review

In the top tabs, select **"Recommendations"**

### 3. Enable AI Recommendations

1. Select a user from the dropdown
2. Expand the **"🤖 AI-Powered Recommendations (OpenAI)"** expandable section
3. Enter your OpenAI API key (get one at https://platform.openai.com/api-keys)
4. Select the model (gpt-4o-mini recommended for cost efficiency)
5. Set the maximum number of recommendations (default: 5)
6. Click the **"🤖 Generate with AI"** button

### 4. Review AI Recommendations

AI-generated recommendations will be displayed with:
- Clear indication of AI source (🤖 AI Generated badge)
- Token usage statistics (shown in notification)
- Same approval/override/flag workflow as rule-based recommendations
- Tone validation results
- Expandable cards for each recommendation with full details

## API Key Security

**Important**: The OpenAI API key is entered in the UI and stored only in the session state. It is NOT saved to disk or committed to the repository.

For production use, consider:
- Using environment variables (OPENAI_API_KEY)
- Implementing secure key management
- Setting up API key rotation policies

## Cost Considerations

OpenAI API usage incurs costs based on token consumption:

- **gpt-4o-mini**: Most cost-effective (~$0.15 per million tokens)
- **gpt-4o**: Higher quality, higher cost (~$5 per million tokens)
- **gpt-3.5-turbo**: Legacy model, lower cost (~$0.50 per million tokens)

Token usage is displayed after each AI generation to help track costs.

## Prompt Engineering

The AI recommendations system uses carefully crafted prompts that:

1. **Provide User Context**: Includes persona, behavioral signals, and account details
2. **Set Constraints**: Enforces educational focus, transparency, and tone guidelines
3. **Require Rationales**: Every recommendation must cite specific user data
4. **Enforce Format**: Returns structured JSON for consistency

See `recommend/ai_recommendations.py` for the full system prompt.

## Guardrails

AI-generated recommendations are subject to the same guardrails as rule-based recommendations:

- **Tone Validation**: Scans for prohibited shaming language
- **Consent Enforcement**: Only generates recommendations for users who have granted consent
- **Disclaimer**: Automatically appends mandatory educational disclaimer
- **Auditability**: All AI recommendations are logged to decision traces

## Troubleshooting

### "OpenAI library not installed"

Run:
```bash
uv pip install openai
```

Or:
```bash
uv sync
```

### "OpenAI API call failed"

- Verify your API key is correct
- Check your OpenAI account has available credits
- Ensure you have internet connectivity
- Check OpenAI API status at https://status.openai.com

### "AI generation failed"

The system will automatically fall back to rule-based recommendations if AI generation fails.

## Comparison: AI vs Rule-Based

| Feature | Rule-Based | AI-Powered |
|---------|-----------|------------|
| **Consistency** | High (deterministic) | Moderate (probabilistic) |
| **Customization** | Fixed templates | Dynamic generation |
| **Cost** | Free | Per-token pricing |
| **Speed** | Fast (<1s) | Moderate (2-5s) |
| **Coverage** | Predefined categories | Flexible topics |
| **Explainability** | Explicit rules | Model-generated |
| **Offline** | Yes | No (requires API) |

## Best Practices

1. **Start with gpt-4o-mini**: Most cost-effective for testing and production
2. **Monitor Token Usage**: Track costs using the displayed token metrics
3. **Use for Complex Cases**: AI excels at nuanced, personalized recommendations
4. **Keep Rule-Based as Default**: Use AI selectively for specific users or cases
5. **Review AI Output**: Always review AI recommendations before approval
6. **Validate Tone**: AI tone validation helps ensure compliance

## Future Enhancements

Potential improvements for future versions:

- Fine-tuned models on financial education data
- Cached API responses for cost optimization
- Batch recommendation generation
- A/B testing framework for AI vs rule-based
- Custom prompt templates per persona
- Integration with user feedback loops

## Technical Details

### Module Location
- **Implementation**: `recommend/ai_recommendations.py`
- **UI Integration**: `ui/app_operator_nicegui.py` (Recommendations tab)

### Key Functions
- `generate_ai_recommendations(user_id, api_key, ...)`: Main entry point
- `_build_prompt_context(user_context, max_recommendations)`: Constructs user-specific prompt
- `_parse_ai_response(ai_response, user_context)`: Validates and structures AI output

### Dependencies
- `openai>=1.0.0`: Official OpenAI Python library

## Support

For issues or questions:
- Check logs in the operator dashboard
- Review decision traces in `docs/traces/`
- Consult `docs/decision_log.md` for operator overrides

---

**Note**: This feature is experimental. Always review AI-generated recommendations for accuracy and compliance before presenting to users.
